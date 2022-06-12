(function(){
    let $ = django.jQuery;
    $(document).ready(function(){
        $('textarea.html-editor').each(function(idx, el){
            CodeMirror.fromTextArea(el, {
                lineNumbers: true,
                lineWrapping: true,
                mode: 'application/ld+json',
                theme: 'seti',
            });
        });
    });
})();
