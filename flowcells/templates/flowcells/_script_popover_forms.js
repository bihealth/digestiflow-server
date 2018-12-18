/**
 * Allow clicking on the states of the flowcell list, display of update for, replace row in table.
 */
$(function () {
  function urlPopOverContent () {
    const div = $('<div>loading</div>')
    const self = $(this)
    const itemRow = $(this).closest('.popover-replace-item')

    $.ajax(
      $(this).data('popover-url'),
      {
        success: function (response) {
          div.html(response);
          $(div).find('.popover-ajax-form').ajaxForm(function (response) {
            self.popover("dispose")
            let newLine = $(response)
            newLine.find('*[data-popover-url]').popover({
              html: true,
              content: urlPopOverContent,
            })
            console.log(newLine.find('*[data-popover-url]'))
            itemRow.replaceWith(newLine)
            if (newLine.data('errors')) {
              $(
                '<div class="alert alert-danger sodar-alert-top mb-3">' +
                '  <div class="sodar-alert-top-content">' +
                newLine.data('errors') +
                '    <a href="#" class="pull-right sodar-alert-close-link"><i class="fa fa-close text-muted"></i></a>' +
                '  </div>' +
                '</div>'
              ).appendTo($('#ajax-form-errors'))
            }
            $('.sodar-alert-close-link').click(function () {
              $(this).closest('.sodar-alert-top').fadeOut('fast');
            });
          })
        }
      }
    )

    return div
  }

  $('.popover-form-container *[data-popover-url]').popover({
    html: true,
    content: urlPopOverContent,
  })
})


/**
 * Handling of error suppression forms that do NOT use `ajaxForm()`
 *
 * We don't use ajaxForm() here but simply do a full post.  Updating is simpler this way.
 */
$(function () {
  function urlPopOverContent () {
    const div = $('<div>loading</div>')

    $.ajax(
      $(this).data('popover-url'),
      {
        success: function (response) {
          console.log(response)
          div.html(response)
        }
      }
    )

    return div
  }

  $('.index-histograms-table *[data-popover-url], .flowcell-properties *[data-popover-url]').popover({
    {#trigger: 'focus',#}
    html: true,
    content: urlPopOverContent,
  })
})