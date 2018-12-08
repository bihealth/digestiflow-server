<template>
  <div>
    <b-row>
      <b-col class="sheet-table-container px-0">
        <hot-table ref="sheetTable" :settings="hotSettings" class="sheet-table"></hot-table>
      </b-col>
    </b-row>
    <!--<b-row>-->
      <!--<b-col>-->
        <!--<b>Please correct the following error(s):</b>-->
        <!--<ul>-->
          <!--<li v-for="error in errors" :key="error.id">{{ error.msg }}</li>-->
        <!--</ul>-->
      <!--</b-col>-->
    <!--</b-row>-->
  </div>
</template>

<script>
import { HotTable } from '@handsontable/vue'
import 'handsontable/dist/handsontable.full.css'
import MultiRange from 'multi-integer-range'
import axios from 'axios'

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
    console.log(_e)
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

export default {
  name: 'SheetEditor',

  props: {
    project: {
      type: String,
      required: true
    }
  },

  data () {
    return {
      barcodesetShortNames: [],
      barcodesets: {},
      onAfterChangeRunning: false,
      // The hidden field whose value will be updated when the grid is updated.
      targetJsonField: null,
      // The original JSON value from the hidden form field.
      originalLibrariesJson: null,
      hotSettings: {
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
        contextMenu: [
          'row_above',
          'row_below',
          'remove_row',
          '---------',
          'copy',
          'cut'
        ],
        copyPaste: true,
        height: 500,
        manualColumnResize: true,
        minSpareRows: 3,
        rowHeaders: true,
        width: '100%',
        wordWrap: false
      },
      errors: []
    }
  },

  mounted () {
    this.targetJsonField = document.getElementById('id_libraries_json')
    this.originalLibrariesJson = JSON.parse(this.targetJsonField.value)
    this.$refs.sheetTable.hotInstance.updateSettings({
      cells: this.hotCells,
      afterChange: this.onAfterChange,
      data: this.getDataFromLibrariesJson(this.originalLibrariesJson)
    })

    // Load barcode sets through API and update HOT settings.
    axios
      .get(`/api/barcodesets/${this.$props.project}/`)
      .then(res => {
        this.barcodesetShortNames = []
        this.barcodesets = {}
        for (var i = 0; i < res.data.length; ++i) {
          this.barcodesets[res.data[i].short_name] = res.data[i]
          this.barcodesetShortNames.push(res.data[i].short_name)
        }
        this.$refs.sheetTable.hotInstance.updateSettings({
          columns: this.hotColumns()
        })
      })
  },

  methods: {
    // Get table data from libraries JSON data
    getDataFromLibrariesJson (jsonData) {
      jsonData.forEach((entry) => {
        
      })
    },

    // Update libraries JSON from Handsontable data
    setLibrariesJsonFromData (origJsonData, tableData) {
      // TODO
    },

    // Called when a cell changed.
    onAfterChange (changes) {
      // Guard against infinite event loop.
      if (this.onAfterChangeRunning) {
        return
      }
      this.onAfterChangeRunning = true

      const hot = this.$refs.sheetTable.hotInstance

      // In the case of selecting barcodes from a barcode set, replace values that are equal to the name of the
      // barcode with its "$name ($sequence)" label that the validator requires.
      changes.forEach(([row, col, oldValue, newValue]) => {
        if (col === 3 || col === 5) {
          const barcodesetVal = hot.getDataAtCell(row, col - 1)
          if (barcodesetVal) {
            const shortName = getShortName(barcodesetVal)
            if (this.barcodesets[shortName]) {
              // TODO could be sped up with lookup table instead of lookup
              // Selected a barcode set, only allow selecting barcodes from set
              this.barcodesets[shortName].entries.forEach((entry) => {
                if (entry.name === newValue) {
                  hot.setDataAtCell(row, col, `${entry.name} (${entry.sequence})`)
                }
              })
            }
          }
        }
      })

      // Push the data into the hidden JSON field.
      this.setLibrariesJsonFromData(this.originalLibrariesJson, hot.getData())

      // Remove "lock" again
      this.onAfterChangeRunning = false
    },

    // Dynamic cell configuration.
    hotCells (row, col, prop) {
      const cellProperties = {}

      if (col === 3 || col === 5) {
        const barcodesetVal = this.$refs.sheetTable.hotInstance.getDataAtCell(row, col - 1)
        if (!barcodesetVal) {
          // Selected "", don't allow editing of barcode
          cellProperties.readOnly = true
          cellProperties.type = 'text'
          cellProperties.className = 'read-only-cell'
        } else {
          const shortName = getShortName(barcodesetVal)
          if (this.barcodesets[shortName]) {
            // Selected a barcode set, only allow selecting barcodes from set
            cellProperties.readOnly = false
            cellProperties.type = 'dropdown'
            cellProperties.source = this.barcodesets[shortName].entries.map(entry => `${entry.name} (${entry.sequence})`)
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
    },

    // Create HOT columns settings based on currently loaded references.
    hotColumns () {
      const labels = ['', 'type barcode -->'].concat(this.barcodesetShortNames.map(shortName => {
        const item = this.barcodesets[shortName]
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
  },

  components: {
    'hot-table': HotTable
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
  .sheet-table-container {
    overflow: hidden;
    height: 500px;
    background-color: #f0f0f0;
  }
</style>
