window.addEventListener("load", () => {
    (($) => {
        const responseTypeDropdown = document.getElementById('id_response_type');
        const responseStatusCodeRow = document.getElementsByClassName('form-row field-response').item(0);
        const httpMethodRow = document.getElementsByClassName('form-row field-method').item(0);
        const proxyToRow = document.getElementsByClassName('form-row field-proxy_destination_address').item(0);

        const showResponseSettings = () => {
            responseStatusCodeRow.hidden = false;
            httpMethodRow.hidden = false;
            proxyToRow.hidden = true;
        }

        const showSingleProxySettings = () => {
            responseStatusCodeRow.hidden = true;
            httpMethodRow.hidden = false;
            proxyToRow.hidden = false;
        }

        const showGlobalProxySettings = () => {
            responseStatusCodeRow.hidden = true;
            httpMethodRow.hidden = true;
            proxyToRow.hidden = false;
        }

        const changeResponseType = () => {
            switch (responseTypeDropdown.value) {
                case 'CUSTOM':
                    showResponseSettings();
                    break;
                case 'PROXY_CURRENT':
                    showSingleProxySettings();
                    break;
                case 'PROXY_GLOBAL':
                    showGlobalProxySettings();
                    break;
            }
        }

        changeResponseType();
        responseTypeDropdown.addEventListener('change', changeResponseType);

    })(django.jQuery);
});
