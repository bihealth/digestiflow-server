// We need quite a bit of state for this so we create an anonymous function for keeping it around.
$(function() {
  /* Original data from the server, kept as a frozen copy in origData;
   *
   * uuid -- UUID from original data, if any
   * name -- Name of the barcode
   * sequence -- Sequence of the barcode
   * status -- One of "unchanged", "changed", "added", "to-remove", "empty"
   */
  var data = JSON.parse($("#id_entries_json").val());

  // Get immutable copy of data into origData.  We need to get this from the Django template because on
  // browser reload, the form field value remains the same once changed.
  const origData = JSON.parse("{{ form.entries_json.value|escapejs }}");
  Object.freeze(origData);
  origData.map(Object.freeze);

  // Variable for storing Handsontable in.
  var hot;

  /**
   * Update the Handsontable and model, update UUID.
   */
  function updateHot() {
    // Collect UUIDs in data and origData
    var dataUuids = data.filter(elem => elem.name).map(elem => elem.uuid).filter(x => x !== null);
    const origDataUuids = origData.map(elem => elem.uuid);
    // Get data by UUID
    var dataByUuid = {};
    for (var i = 0; i < data.length; ++i) {
      dataByUuid[data[i].uuid] = data[i];
    }
    // Get orig data by name and UUID
    var origDataByUuid = {};
    var origDataByName = {};
    for (var i = 0; i < origData.length; ++i) {
      origDataByName[origData[i].name] = origData[i];
      origDataByUuid[origData[i].uuid] = origData[i];
    }

    // Try to match back UUIDs to data based on name, prevent assignment of duplicate
    for (var i = 0; i < data.length; ++i) {
      if (!data[i].uuid && data[i].name) {
        const candidateOrig = origDataByName[data[i].name];  // candidate in origData
        if (candidateOrig && !dataUuids.includes(candidateOrig.uuid)) {  // UUID free in data?
          dataByUuid[candidateOrig.uuid].uuid = null;  // assigned to data[i] now!
          data[i].uuid = candidateOrig.uuid;
          dataUuids.push(candidateOrig.uuid);
        }
      }
    }
    // Update "status" column
    for (var i = 0; i < data.length; ++i) {
      if (data[i].uuid && data[i].name) {
        if (origDataByUuid[data[i].uuid].name != data[i].name ||
          origDataByUuid[data[i].uuid].sequence != data[i].sequence) {
          data[i].status = "changed";
        } else {
          data[i].status = "unchanged";
        }
      } else if (data[i].uuid && !data[i].name) {
        data[i].status = "to-remove"
      } else if (!data[i].uuid && data[i].name) {
        data[i].status = "added";
      } else if (!data[i].uuid && !data[i].name) {
        data[i].status = null;
      }
    }

    if (hot) {
      hot.render();
    }
  }

  function updateActionPreview() {
    var origDataByUuid = {};
    for (var i = 0; i < origData.length; ++i) {
      origDataByUuid[origData[i].uuid] = origData[i];
    }

    var ul = $("<ul></ul>");
    for (var i = 0; i < data.length; ++i) {
      if (data[i].status == "empty" || data[i].status == "unchanged") {
        // no-op
      } else if (data[i].status == "changed") {
        console.log("i = " + i + " changed");
        const curr = data[i];
        const orig = origDataByUuid[curr.uuid];
        var txt = "Will update barcode \"" + orig.name + "\".";
        if (curr.name != orig.name) {
          txt += " Will set name to \"" + curr.name + "\".";
        }
        if (curr.sequence != orig.sequence) {
          txt += " Will set sequence to \"" + curr.sequence + "\".";
        }
        ul.append($("<li></li>").text(txt));
      } else if (data[i].status == "added") {
        ul.append($("<li></li>").text("Will add barcode " + data[i].name + " with sequence \"" + data[i].sequence + "\""));
      } else if (data[i].status == "to-remove") {
        ul.append($("<li></li>").text("Will remove barcode \"" + origDataByUuid[data[i].uuid] + "\""))
      }
    }

    // Add empty list entry.
    if (!ul.children().length) {
      ul.append($("<li></li>").text("No change to barcodes"))
    }

    $("#id-action-preview").html(ul);
  }

  // Guard against calling `onChangeHandler()` twice.
  var onChangeRunning = false;

  function onChangeHandler() {
    // Prevent on-change handler from firing recursively.
    if (onChangeRunning) {
      return;
    }
    onChangeRunning = true;

    updateHot();
    updateActionPreview();
    writeData();

    onChangeRunning = false;
  }

  /**
   * Initialize Handsontable
   */
  const container = document.getElementById('barcodeSetEntryGrid');
  hot = new Handsontable(container, {
    colHeaders: ['name', 'sequence', 'status'],
    columns: [
      {data: 'name'},
      {data: 'sequence'},
      {data: 'status', editor: false}
    ],
    colWidths: [150, 200, 100],
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
                  let oldValue = this.getDataAtCell(row, 1);
                  this.setDataAtCell(row, 1, revComp(oldValue));
                }
              }
            }
          }
        }
      }
    },
    data: data,
    dataSchema: {uuid: null, name: null, sequence: null, status: null},
    height: 500,
    manualColumnResize: true,
    minSpareRows: 3,
    outsideClickDeselects: false,
    rowHeaders: true,
    width: "100%",
    afterInit: onChangeHandler,
    afterChange: onChangeHandler
  });
  setTimeout(function() { hot.render() }, 500)

  /**
   * Reverse-complement string.
   */
  function revComp(seq) {
    function complement(a) {
      return {A: 'T', T: 'A', G: 'C', C: 'G'}[a];
    }

    return seq.split('').reverse().map(complement).join('');
  }

  /**
   * Write data to hidden field.
   */
  function writeData() {
    const nonEmpty = data.filter(elem => elem.name);
    $("#id_entries_json").val(JSON.stringify(nonEmpty));
  }
});
