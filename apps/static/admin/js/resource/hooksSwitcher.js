// Setting up hooks settings visibility according to the hook type.

window.addEventListener("load", () => {
    (($) => {
        if (location.pathname.indexOf('add') === -1 && location.pathname.indexOf('change') === -1) {
            return
        }

        /* For some reason, in the Safari browser, the inline containing the list of hooks is loading late.
        That's why we have to wait for the specific web elements to deal with. */

        const addHookLinkSelector = "a:contains('Add another Hook')";
        const hooksRowsSelector = ".dynamic-hooks";

        const getBelatedElement = (selector, callback, timeout = 2000) => {
            const start = Date.now();
            let interval = setInterval(() => {
                const element = $(selector)
                if (element) {
                    clearInterval(interval);
                    callback(element);
                } else if (Date.now() - start > timeout) {
                    clearInterval(interval);
                    callback(null);
                }
            }, 100);
        };

        const changeHookSettingsVisibility = (hooksRow) => {
            let actionElement = document.getElementById(`id_${hooksRow.id}-action`)
            let requestElement = document.getElementById(`id_${hooksRow.id}-request`)
            let addRequest = document.getElementById(`add_id_${hooksRow.id}-request`)
            let changeRequest = document.getElementById(`change_id_${hooksRow.id}-request`)
            let hookTimeout = document.getElementById(`id_${hooksRow.id}-timeout`)

            if (actionElement.value === 'webhook') {
                hookTimeout.hidden = true;
                requestElement.hidden = false;
                addRequest.hidden = false;
                changeRequest.hidden = false;
            } else {
                hookTimeout.hidden = false;
                requestElement.value = '';
                requestElement.hidden = true;
                addRequest.hidden = true;
                changeRequest.hidden = true;
            }
        };

        const setHookSettingsVisibilityByEvent = (event) => {
            const hooksRow = event.data.rowElement;
            changeHookSettingsVisibility(hooksRow);
        };

        const refreshHookSettingsVisibility = () => {
            $(hooksRowsSelector).each(function() {
                changeHookSettingsVisibility($( this )[0]);
            });
        };

        const setEventToEachHookTypeDropdown = (hooksRows) => {
            for (const hook of hooksRows) {
                $(`#id_${hook.id}-action`).on("change", {
                    rowElement: hook
                }, setHookSettingsVisibilityByEvent);
            }
        };

        const resetHookSettingsVisibility = () => {
            getBelatedElement(hooksRowsSelector, setEventToEachHookTypeDropdown);
            refreshHookSettingsVisibility();
        };

        const setEventToAddHookLink = (element) => {
            element[0].addEventListener('click', resetHookSettingsVisibility);
            refreshHookSettingsVisibility();
        };

        getBelatedElement(addHookLinkSelector, setEventToAddHookLink);
        getBelatedElement(hooksRowsSelector, setEventToEachHookTypeDropdown);

    })(django.jQuery);
});
