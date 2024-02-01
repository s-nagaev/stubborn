window.addEventListener("load", () => {
    (($) => {
        const fileBtn = $("#file-btn")

        function getCookie() {
            const cookie_array = document.cookie.split(';')
            const csrf_cookie_row = cookie_array.filter(cookie => cookie.includes('csrftoken'))[0]
            const csrf_cookie_value = csrf_cookie_row.split('=')[1]
            return csrf_cookie_value
        }

        function sendFile(update=false) {
            const token = getCookie()
            const formData = new FormData();
            formData.append('file', fileBtn[0].files[0]);

            if (update) {
                formData.append('update', true)
            }

            $.ajax({
                   url : '/srv/import/',
                   type : 'POST',
                   data : formData,
                   headers: {
                    'X-CSRFToken': token
                   },
                   processData: false,
                   contentType: false,
                   success : (data) => {
                       location.reload();
                   },
                   error : (data) => {
                       if (data.responseText.includes('already exists')) {
                           const update = confirm('Do you want to update an existing Application?');
                           if (update) {
                               sendFile(true);
                           }
                       }
                   }
            });
        }

        fileBtn.on("change", () => {
            sendFile()
        })
    })(django.jQuery)
});
