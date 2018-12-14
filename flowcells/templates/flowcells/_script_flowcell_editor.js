// Validate a sample name.
function sampleNameValidator (query, report) {
  if (!query) {
    report(true)
  } else {
    report(query.match(/^[a-zA-Z0-9_-]+$/) !== null)
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

$(function () {

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
      'lanes'
    ],
    colWidths: [
      100,
      100,
      200,
      100,
      200,
      100,
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
        'sep2': Handsontable.plugins.ContextMenu.SEPARATOR,
        'reverse_complement': {
          name: 'Reverse-complement',
          callback: function() {
            let sel = this.getSelectedRange();
            for (var i = 0; i < sel.length; ++i) {
              let frmCol = Math.min(sel[i].from.col, sel[i].to.col)
              let toCol = Math.max(sel[i].from.col, sel[i].to.col)
              let frmRow = Math.min(sel[i].from.row, sel[i].to.row)
              let toRow = Math.max(sel[i].from.row, sel[i].to.row)
              for (var col = frmCol; col <= toCol; ++col) {
                for (var row = frmRow; row <= toRow; ++row) {
                  if (col == 3 || col == 5) {
                    if (this.getDataAtCell(row, col - 1) == 'type barcode -->') {
                      this.setDataAtCell(row, col, revComp(this.getDataAtCell(row, col)));
                    }
                  }
                }
              }
            }
          }
        },
        'name_lookup' : {
          name: 'Re-do name lookup',
          callback: function() {
            let sel = this.getSelectedRange();
            for (var i = 0; i < sel.length; ++i) {
              let frmCol = Math.min(sel[i].from.col, sel[i].to.col)
              let toCol = Math.max(sel[i].from.col, sel[i].to.col)
              let frmRow = Math.min(sel[i].from.row, sel[i].to.row)
              let toRow = Math.max(sel[i].from.row, sel[i].to.row)
              for (var col = frmCol; col <= toCol; ++col) {
                for (var row = frmRow; row <= toRow; ++row) {
                  if (col == 3 || col == 5) {
                    performNameLookup(row, col, this.getDataAtCell(row, col))
                  }
                }
              }
            }
          }
        }
      }
    },
    copyPaste: true,
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
      setTimeout(function() { hotTable.render() }, 200)
    })

  // Get table data from libraries JSON data
  function getDataFromLibrariesJson (jsonData) {
    // Disable onAfterChange handler
    onAfterChangeRunning = true

    jsonData.forEach((entry, row) => {
      hotTable.setDataAtCell(row, 0, entry.name)
      hotTable.setDataAtCell(row, 1, entry.reference)

      if (entry.barcode_seq) {
        hotTable.setDataAtCell(row, 2, 'type barcode -->')
        hotTable.setDataAtCell(row, 3, entry.barcode_seq)
      } else if (entry.barcode) {
        const barcode = barcodes[entry.barcode]
        const barcodeset = barcodesets[barcode.barcode_set]
        hotTable.setDataAtCell(row, 2, `${barcodeset.name} (${barcodeset.short_name})`)
        hotTable.setDataAtCell(row, 3, `${barcode.name} (${barcode.sequence})`)
      }

      if (entry.barcode_seq2) {
        hotTable.setDataAtCell(row, 4, 'type barcode -->')
        hotTable.setDataAtCell(row, 5, entry.barcode_seq2)
      } else if (entry.barcode2) {
        const barcode = barcodes[entry.barcode]
        const barcodeset = barcodesets[barcode.barcode_set]
        hotTable.setDataAtCell(row, 2, `${barcodeset.name} (${barcodeset.short_name})`)
        hotTable.setDataAtCell(row, 3, `${barcode.name} (${barcode.sequence})`)
      }

      const numbers = new MultiRange()
      entry.lane_numbers.forEach((x) => numbers.append(x))
      hotTable.setDataAtCell(row, 6, numbers.toString())
    })

    // Enable onAfterChange handler again
    onAfterChangeRunning = false
  }

  // Update libraries JSON from Handsontable data
  function setLibrariesJsonFromData (origJsonData, tableData) {
    const jsonData = tableData
      .filter((row) => !!row[0])
      .map(([name, reference, barcodeset, barcodeVal, barcodeset2, barcodeVal2, lanes]) => {
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
          lane_numbers: lanesArr
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
      }
    ]
  }

})
