window.addEventListener("load", () => {
    (($) => {
        const destinationAddressField = document.getElementById('id_proxy_destination_address');
        const responseDropdown = document.getElementById('id_response');
        const changeResponsePic = document.getElementById('change_id_response');
        
        const changeDropdownActivity = () => {
            if (destinationAddressField.value === '') {
                responseDropdown.disabled = false;
                changeResponsePic.hidden = false;
                responseDropdown.style.textDecoration=null;
            } else {
                responseDropdown.disabled = true;
                changeResponsePic.hidden = true;
                responseDropdown.style.textDecoration='line-through';
            }
        }
        changeDropdownActivity();
        destinationAddressField.addEventListener('change', changeDropdownActivity);
    })(django.jQuery);
});
