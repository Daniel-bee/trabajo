const badge = [
    'badge text-bg-primary',
    'badge text-bg-secondary',
    'badge text-bg-success',
    'badge text-bg-danger',
    'badge text-bg-warning',
    'badge text-bg-info',
    'badge text-bg-dark'
    ]   
$(".badged" ).each(function() {
    let rand_num = Math.floor(Math.random() * 7)
    $(this).addClass(badge[rand_num])
})