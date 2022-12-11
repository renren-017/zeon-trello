for (element of document.getElementsByClassName('column')) {
        new Dragster(element);
        element.addEventListener('dragover', e => {
            if (e.preventDefault) e.preventDefault();
        });
        element.addEventListener('dragster:enter', e => {
            e.currentTarget.classList.add('dropme')
        });
        element.addEventListener('dragster:leave', e => {
            e.currentTarget.classList.remove('dropme')
        });
        element.addEventListener('drop', e => {
            e.currentTarget.classList.remove('dropme')
            const postData = JSON.stringify({
                'column_id': e.currentTarget.dataset.columnId,
                'card_id': e.dataTransfer.getData('Text'),
            });

            fetch('/drop/', {
                credentials: 'same-origin',
                method: 'post',
                headers: {
                    'X-CSRFToken': cookies['csrftoken'],
                },
                body: postData,
            }).then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    alert('Error! ' + response.statusText);
                }
            }).catch(err => {
                console.log(err);
            });

        });