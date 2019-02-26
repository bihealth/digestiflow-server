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

  // Setup header information.
  const headers = [
    {name: "name", label: "name", column: 0, width: 100},
    {name: "reference", label: "organism", column: 1, width: 100},
    {name: "barcodeSet1", label: "i7 kit", column: 2, width: 200},
    {name: "barcode1", label: "i7 sequence", column: 3, width: 100},
    {name: "barcodeSet2", label: "i5 kit", column: 4, width: 200},
    {name: "barcode2", label: "i5 sequence", column: 5, width: 100},
    {name: "lanes", label: "lane(s)", column: 6, width: 60},
    {name: "customDemux", label: "[custom cycles]", column: 7, width: 100},
  ];
  // Map from header column name to column
  const headerNameToCol = new Map()
  for (let e of headers) {
    headerNameToCol.set(e.name, e.column)
  }

  // Shortcuts to column indices
  const nameCol = headerNameToCol.get("name")
  const organismCol = headerNameToCol.get("reference")
  const barcodeSet1Col = headerNameToCol.get("barcodeSet1")
  const barcode1Col = headerNameToCol.get("barcode1")
  const barcodeSet2Col = headerNameToCol.get("barcodeSet2")
  const barcode2Col = headerNameToCol.get("barcode2")
  const lanesCol = headerNameToCol.get("lanes")
  const customDemuxCol = headerNameToCol.get("customDemux")

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
    colHeaders: headers.map(e => e.label),
    colWidths: headers.map(e => e.width),
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
              if (col == barcode1Col || col == barcode2Col) {
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
              if (col == barcode1Col) {
                performNameLookup(row, col, barcodeSet1Col, this.getDataAtCell(row, col))
              } else if (col == barcode2Col) {
                performNameLookup(row, col, barcodeSet2Col, this.getDataAtCell(row, col))
              }
            }
            forEachInRange(this.getSelectedRange(), callback.bind(this))
          }
        },
        'replace_bad_chars': {
          name: 'Fix sample names',
          callback: function() {
            function callback (row, col) {
              if (col == nameCol) {
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
      }, 500)
    })

  // Get table data from libraries JSON data
  function getDataFromLibrariesJson (jsonData) {
    const result = new Array();

    jsonData.forEach((entry, _) => {
      const row = ['', '', '', '', '', '', '', '', '']
      row[headerNameToCol.get("name")] = entry.name
      row[headerNameToCol.get("reference")] = entry.reference

      if (entry.barcode_seq) {
        row[headerNameToCol.get("barcodeSet1")] = 'type barcode -->'
        row[headerNameToCol.get("barcode1")] = entry.barcode_seq
      } else if (entry.barcode) {
        const barcode = barcodes[entry.barcode]
        const barcodeset = barcodesets[barcode.barcode_set]
        row[headerNameToCol.get("barcodeSet1")] = `${barcodeset.name} (${barcodeset.short_name})`
        row[headerNameToCol.get("barcode1")] = `${barcode.name} (${barcode.sequence})`
      }

      if (entry.barcode_seq2) {
        row[headerNameToCol.get("barcodeSet2")] = 'type barcode -->'
        row[headerNameToCol.get("barcode2")] = entry.barcode_seq2
      } else if (entry.barcode2) {
        const barcode2 = barcodes[entry.barcode2]
        const barcodeset2 = barcodesets[barcode2.barcode_set]
        row[headerNameToCol.get("barcodeSet2")] = `${barcodeset.name} (${barcodeset2.short_name})`
        row[headerNameToCol.get("barcode2")] = `${barcode2.name} (${barcode2.sequence})`
      }

      const numbers = new MultiRange()
      entry.lane_numbers.forEach((x) => numbers.append(x))
      row[headerNameToCol.get("lanes")] = numbers.toString()

      row[headerNameToCol.get("customDemux")] = entry.demux_reads

      result.push(row)
    })

    return result
  }

  // Update libraries JSON from Handsontable data
  function setLibrariesJsonFromData (origJsonData, tableData) {
    const jsonData = tableData
      .filter((row) => !!row[0])
      .map(row => {
        const name = row[nameCol]
        const reference = row[organismCol]
        const barcodeSet1 = row[barcodeSet1Col]
        const barcode1 = row[barcode1Col]
        const barcodeSet2 = row[barcodeSet2Col]
        const barcode2 = row[barcode2Col]
        const lanes = row[lanesCol]
        const demuxReads = row[customDemuxCol]

        let lanesArr
        try {
          lanesArr = new MultiRange(lanes).toArray()
        } catch (e) {
          lanesArr = []
        }

        let barcodeUuid = null
        let barcodeSeq = null
        if (barcodeSet1 === 'type barcode -->') {
          barcodeSeq = barcode1
        } else if (barcodeSet1) {
          const barcodeSet = barcodesetByShortName[getShortName(barcodeSet1)]
          const barcode = barcodeSet.entries.find((entry) => {
            return barcode1 === `${entry.name} (${entry.sequence})`
          })
          if (barcode) {
            barcodeUuid = barcode.sodar_uuid
          }
        }

        let barcodeUuid2 = null
        let barcodeSeq2 = null
        if (barcodeSet2 === 'type barcode -->') {
          barcodeSeq2 = barcode2
        } else if (barcodeSet2) {
          const barcodeSet = barcodesetByShortName[getShortName(barcodeSet2)]
          const barcode = barcodeSet.entries.find((entry) => {
            return barcode2 === `${entry.name} (${entry.sequence})`
          })
          if (barcode) {
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
  function performNameLookup(row, col, setCol, newValue) {
    const barcodesetVal = hotTable.getDataAtCell(row, setCol)
    if (barcodesetVal) {
      const shortName = getShortName(barcodesetVal)
      if (barcodesetByShortName[shortName]) {
        // TODO could be sped up with lookup table instead of lookup
        // Selected a barcode set, only allow selecting barcodes from set
        barcodesetByShortName[shortName].entries.forEach((entry) => {
          if (entry.name === newValue || entry.aliases.indexOf(newValue) > -1) {
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
      if (col == barcode1Col) {
        performNameLookup(row, col, barcodeSet1Col, newValue)
      } else if (col == barcode2Col) {
        performNameLookup(row, col, barcodeSet2Col, newValue)
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

    if (col === barcode1Col || col === barcode2Col) {
      let barcodeSetCol = null
      if (col == barcode1Col) {
        barcodeSetCol = barcodeSet1Col
      } else {
        barcodeSetCol = barcodeSet2Col
      }

      const barcodesetVal = hotTable.getDataAtCell(row, barcodeSetCol)
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
          cellProperties.source = barcodesetByShortName[shortName].entries.map(
            entry => `${entry.name} (${entry.sequence})`)
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
    const result = []
    for (var i = 0; i <= 7; ++i) {
      switch (headers[i].name) {
        case "name":
          result.push({validator: sampleNameValidator})
          break;
        case "reference":
          result.push({type: 'autocomplete', source: references.map(ref => ref.label)})
          break;
        case "barcodeSet1":
        case "barcodeSet2":
          result.push({type: 'dropdown', source: labels})
          break;
        case "lanes":
          result.push({validator: integerRangeValidator})
          break;
        case "customDemux":
          result.push({validator: demuxValidator})
          break;
        case "barcode1":
        case "barcode2":
          result.push({})
          break;
        default:
          console.error("Invalid header name", headers[i].name)
          result.push({})
      }
    }
    return result
  }

})
