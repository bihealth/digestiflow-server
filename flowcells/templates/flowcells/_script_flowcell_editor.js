// Validate a sample name.
function sampleNameValidator (query, report) {
  if (!query) {
    report(true)
  } else {
    report(query.match(/^[a-zA-Z0-9_-]+$/) !== null)
  }
}

// Validate a demultiplexing string.
function demuxValidator (query, report) {
  if (!query) {
    report(true)
  } else {
    report(query.match(/^(\d+[BMTSbmts])*$/) !== null)
  }
}

// Validate a barcode or list thereof
function barcodeValidator (query, report) {
  if (!query) {
    return true
  } else {
    const regexp = /^[acgtnACGTN]+(,[acgtnACGTN]+)*$/
    report(query.match(regexp) !== null)
  }
}

// Validate an integer range.
function integerRangeValidator (query, report) {
  if (!query) {
    // allow empty field
    report(true)
    return
  }
  try {
    new MultiRange(query) // eslint-disable-line
  } catch (_e) {
    report(false)
    return
  }
  report(true)
}

// Extract short name from a barcode label
function getShortName (val) {
  const regexp = /^.*\((.*)\)$/g
  const match = regexp.exec(val)
  if (match) {
    return match[1]
  } else {
    return ''
  }
}

// The reference choices availabel at the moment.
let references = [
  {key: 'hg19', label: 'human'},
  {key: 'mm9', label: 'mouse'},
  {key: 'dm6', label: 'fly'},
  {key: 'danRer6', label: 'zebrafish'},
  {key: 'rn1', label: 'rat'},
  {key: 'cel1', label: 'worm'},
  {key: 'sacCer3', label: 'yeast'},
  {key: '__other__', label: 'other'}
]

// Mapping reference label to key
let labelToReference = {}
references.forEach((entry) => {
  labelToReference[entry.label] = entry.key
})

function forEachInRange(sel, callback) {
  for (let i = 0; i < sel.length; ++i) {
    let frmCol = Math.min(sel[i].from.col, sel[i].to.col)
    let toCol = Math.max(sel[i].from.col, sel[i].to.col)
    let frmRow = Math.min(sel[i].from.row, sel[i].to.row)
    let toRow = Math.max(sel[i].from.row, sel[i].to.row)
    for (let col = frmCol; col <= toCol; ++col) {
      for (let row = frmRow; row <= toRow; ++row) {
        callback(row, col)
      }
    }
  }
}

$(function () {

  // Clipboard handling...
  var clipboardCache = '';

  // Barcode sets by UUID
  var barcodesets = {}
  // Short names of barcode sets
  var barcodesetShortNames = []
  // Barcode sets by short name
  var barcodesetByShortName = {}
  // Barcodes by their UUID
  var barcodes = {}

  // Instance of the Handsontable
  var hotTable
  // Flag for preventing running on HOT change handler recursively
  var onAfterChangeRunning = true
  // Settings for the Handsontable
  var hotSettings = {
    afterChange: onAfterChange,
    allowInsertRow: true,
    allowRemoveRow: true,
    allowInsertColumn: false,
    allowRemoveColumn: false,
    colHeaders: [
      'name',
      'reference',
      'barcode set #1',
      'barcode #1',
      'barcode set #2',
      'barcode #2',
      'lanes',
      'custom demux'
    ],
    colWidths: [
      100,
      100,
      200,
      100,
      200,
      100,
      60,
      100
    ],
    columnSorting: false,
    contextMenu: {
      items: {
        'row_above': {},
        'row_below': {},
        'remove_row': {},
        'sep1': Handsontable.plugins.ContextMenu.SEPARATOR,
        'copy': {},
        'cut': {},
        'paste': {
          name: 'Paste',
          disabled: function() {
            return clipboardCache.length === 0;
          },
          callback: function() {
            var plugin = this.getPlugin('copyPaste');

            this.listen();
            plugin.paste(clipboardCache);
          }
        },
        'sep2': Handsontable.plugins.ContextMenu.SEPARATOR,
        'reverse_complement': {
          name: 'Reverse-complement',
          callback: function() {
            function callback (row, col) {
              if (col == 3 || col == 5) {
                this.setDataAtCell(row, col, revComp(this.getDataAtCell(row, col)));
              }
            }
            forEachInRange(this.getSelectedRange(), callback.bind(this))
          }
        },
        'name_lookup' : {
          name: 'Re-do name lookup',
          callback: function() {
            function callback (row, col) {
              if (col == 3 || col == 5) {
                performNameLookup(row, col, this.getDataAtCell(row, col))
              }
            }
            forEachInRange(this.getSelectedRange(), callback.bind(this))
          }
        },
        'replace_bad_chars': {
          name: 'Fix sample names',
          callback: function() {
            function callback (row, col) {
              if (col == 0) {
                this.setDataAtCell(row, col, this.getDataAtCell(row, col).replace(/[^a-zA-Z0-9_-]/g, '_'))
              }
            }
            forEachInRange(this.getSelectedRange(), callback.bind(this))
          }
        }
      }
    },
    copyPaste: true,
    afterCopy: function(changes) {
      clipboardCache = SheetClip.stringify(changes);
    },
    afterCut: function(changes) {
      clipboardCache = SheetClip.stringify(changes);
    },
    afterPaste: function(changes) {
      // we want to be sure that our cache is up to date, even if someone pastes data from another source than our tables.
      clipboardCache = SheetClip.stringify(changes);
    },
    height: 500,
    manualColumnResize: true,
    minSpareRows: 3,
    rowHeaders: true,
    width: '100%',
    wordWrap: false
  }

  // Errors collection
  var errors = []

  // Arguments, currently only the project UUID
  let args = JSON.parse(document.getElementById('hot-table').attributes['data-args'].value)
  var project = args['project']
  // The JSON field we move the sample sheet JSON with back and forth
  var targetJsonField = document.getElementById('id_libraries_json')
  // The original form value.  We need to keep this as on reload, the browser will replace any changed value
  // in targetJsonField before we have a chance to read it.
  var originalLibrariesJson = JSON.parse(targetJsonField.value)

  // Load barcode sets through API and update HOT settings.  Afterwards, we can load the data libraries from
  // JSON.
  //
  // The initialization of the Handsontable object is here!
  axios
    .get(`/api/barcodesets/${project}/`)
    .then(res => {
      barcodesetShortNames = []
      barcodesetByShortName = {}
      barcodesets = {}
      barcodes = {}
      for (var i = 0; i < res.data.length; ++i) {
        barcodesetByShortName[res.data[i].short_name] = res.data[i]
        barcodesets[res.data[i].sodar_uuid] = res.data[i]
        barcodesetShortNames.push(res.data[i].short_name)
        res.data[i].entries.forEach((barcode) => {
          barcodes[barcode.sodar_uuid] = barcode
        })
      }

      let container = document.getElementById('hot-table')
      hotTable = new Handsontable(container, hotSettings)
      hotTable.updateSettings({
        columns: hotColumns(),
        data: getDataFromLibrariesJson(originalLibrariesJson),
        cells: hotCells
      })
      onAfterChangeRunning = false
      setTimeout(function() {
        hotTable.validateCells()
        hotTable.render()
      }, 200)
    })

  // Get table data from libraries JSON data
  function getDataFromLibrariesJson (jsonData) {
    const result = new Array();

    jsonData.forEach((entry, _) => {
      const row = new Array()
      row.push(entry.name)
      row.push(entry.reference)

      if (entry.barcode_seq) {
        row.push('type barcode -->')
        row.push(entry.barcode_seq)
      } else if (entry.barcode) {
        const barcode = barcodes[entry.barcode]
        const barcodeset = barcodesets[barcode.barcode_set]
        row.push(`${barcodeset.name} (${barcodeset.short_name})`)
        row.push(`${barcode.name} (${barcode.sequence})`)
      } else {
        row.push("")
        row.push("")
      }

      if (entry.barcode_seq2) {
        row.push('type barcode -->')
        row.push(entry.barcode_seq2)
      } else if (entry.barcode2) {
        const barcode2 = barcodes[entry.barcode2]
        const barcodeset2 = barcodesets[barcode2.barcode_set]
        row.push(`${barcodeset.name} (${barcodeset2.short_name})`)
        row.push(`${barcode2.name} (${barcode2.sequence})`)
      } else {
        row.push("")
        row.push("")
      }

      const numbers = new MultiRange()
      entry.lane_numbers.forEach((x) => numbers.append(x))
      row.push(numbers.toString())

      row.push(entry.demux_reads)

      console.log(row)

      result.push(row)
    })

    return result
  }

  // Update libraries JSON from Handsontable data
  function setLibrariesJsonFromData (origJsonData, tableData) {
    const jsonData = tableData
      .filter((row) => !!row[0])
      .map(([name, reference, barcodeset, barcodeVal, barcodeset2, barcodeVal2, lanes, demuxReads]) => {
        let lanesArr
        try {
          lanesArr = new MultiRange(lanes).toArray()
        } catch (e) {
          lanesArr = []
        }

        let barcodeUuid = null
        let barcodeSeq = null
        if (barcodeset === 'type barcode -->') {
          barcodeSeq = barcodeVal
        } else if (barcodeset) {
          const barcodeSet = barcodesetByShortName[getShortName(barcodeset)]
          const barcode = barcodeSet.entries.find((entry) => {
            return barcodeVal === `${entry.name} (${entry.sequence})`
          })
          if (barcode) {
            barcodeUuid = barcode.sodar_uuid
          }
        }

        let barcodeUuid2 = null
        let barcodeSeq2 = null
        if (barcodeset2 === 'type barcode -->') {
          barcodeSeq2 = barcodeVal2
        } else if (barcodeset2) {
          const barcodeSet2 = barcodesetByShortName[getShortName(barcodeset2)]
          const barcode2 = barcodeSet2.entries.find((entry) => {
            return barcodeVal2 === `${entry.name} (${entry.sequence})`
          })
          if (barcode2) {
            barcodeUuid2 = barcode2.sodar_uuid
          }
        }

        return {
          name: name,
          reference: reference,
          barcode: barcodeUuid,
          barcode_seq: barcodeSeq,
          barcode2: barcodeUuid2,
          barcode_seq2: barcodeSeq2,
          lane_numbers: lanesArr,
          demux_reads: demuxReads
        }
      })

    targetJsonField.value = JSON.stringify(jsonData)
  }

  // Performs lookup for the given cell.
  function performNameLookup(row, col, newValue) {
    const barcodesetVal = hotTable.getDataAtCell(row, col - 1)
    if (barcodesetVal) {
      const shortName = getShortName(barcodesetVal)
      if (barcodesetByShortName[shortName]) {
        // TODO could be sped up with lookup table instead of lookup
        // Selected a barcode set, only allow selecting barcodes from set
        barcodesetByShortName[shortName].entries.forEach((entry) => {
          if (entry.name === newValue) {
            hotTable.setDataAtCell(row, col, `${entry.name} (${entry.sequence})`)
          }
        })
      }
    }
  }

  // Called when a cell changed.
  function onAfterChange (changes) {
    // Guard against infinite event loop.
    if (!changes || onAfterChangeRunning) {
      return
    }
    onAfterChangeRunning = true

    // In the case of selecting barcodes from a barcode set, replace values that are equal to the name of the
    // barcode with its "$name ($sequence)" label that the validator requires.
    changes.forEach(([row, col, oldValue, newValue]) => {
      if (col === 3 || col === 5) {
        performNameLookup(row, col, newValue);
      }
    })

    // Push the data into the hidden JSON field.
    setLibrariesJsonFromData(originalLibrariesJson, hotTable.getData())

    // Remove "lock" again
    onAfterChangeRunning = false
  }

  // Dynamic cell configuration.
  function hotCells (row, col, prop) {
    const cellProperties = {}

    if (col === 3 || col === 5) {
      const barcodesetVal = hotTable.getDataAtCell(row, col - 1)
      if (!barcodesetVal) {
        // Selected "", don't allow editing of barcode
        cellProperties.readOnly = true
        cellProperties.type = 'text'
        cellProperties.className = 'read-only-cell'
      } else {
        const shortName = getShortName(barcodesetVal)
        if (barcodesetByShortName[shortName]) {
          // Selected a barcode set, only allow selecting barcodes from set
          cellProperties.readOnly = false
          cellProperties.type = 'dropdown'
          cellProperties.source = barcodesetByShortName[shortName].entries.map(entry => `${entry.name} (${entry.sequence})`)
          cellProperties.className = ''
          cellProperties.validator = 'dropdown'
        } else {
          // Allowing manual entering of barcodes
          cellProperties.readOnly = false
          cellProperties.type = 'text'
          cellProperties.className = ''
          cellProperties.validator = barcodeValidator
        }
      }
    }

    return cellProperties
  }

  // Create HOT columns settings based on currently loaded references.
  function hotColumns () {
    const labels = ['', 'type barcode -->'].concat(barcodesetShortNames.map(shortName => {
      const item = barcodesetByShortName[shortName]
      return `${item.name} (${item.short_name})`
    }))
    return [
      // name
      {
        validator: sampleNameValidator
      },
      // reference
      {
        type: 'autocomplete',
        source: references.map(ref => ref.label)
      },
      // barcode set 1
      {
        type: 'dropdown',
        source: labels
      },
      // barcode 1
      {},
      // barcode set 2
      {
        type: 'dropdown',
        source: labels
      },
      // barcode 2
      {},
      // lanes
      {
        validator: integerRangeValidator
      },
      // custom demux
      {
        validator: demuxValidator
      }
    ]
  }

})
