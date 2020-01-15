function show_toast(header, body, color = 'black') {
    $('.toast-header').text(header);
    $('.toast-body').text(body);
    $('.toast-body').attr('style', `color:${color};`);
    $('.toast').toast('show');
}