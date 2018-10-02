$('#intro').collapse('show')

$('section').on('show.bs.collapse', function (e) {
  $('section').collapse('hide')
  $('.nav-item').removeClass('active')
  $("a[href$=" + e.target.id + "]").parent().addClass('active')
})