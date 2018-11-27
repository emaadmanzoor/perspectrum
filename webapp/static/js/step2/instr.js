$(document).ready(function() {
    $('#instr_submit').click(submit);
});

/**
 * TODO: django rotates CSRF token after login(), so if you click login twice, CSRF token check will fail.
 * https://gist.github.com/j4mie/9055969
 */
function submit() {
    csrfSetup();

    $.post("/step2/api/submit_instr/", {}, instr_callback);
}

function instr_callback() {
    window.location.href = '/step2/task_list';
}