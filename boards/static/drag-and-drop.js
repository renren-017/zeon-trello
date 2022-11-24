function dragOverHandler(e) {
    e.preventDefault()
    if (e.target.className == 'job-block') {
        e.target.style.BoxShadow = '0 2px 3px gray'
    }
}

function dragLeaveHandler(e) {
    e.target.style.BoxShadow = 'none'
}

function dragStartHandler(e) {
}

function dragEndHandler(e) {
    e.target.style.BoxShadow = 'none'
}

function dropHandler(e) {
    e.preventDefault()
}

const elem = document.getElementById('card');

elem.ondragover = (e) => dragOverHandler(e)
elem.ondragleave = (e) => dragLeaveHandler(e)
elem.ondragstart = (e) => dragStartHandler(e)
elem.ondragend = (e) => dragEndHandler(e)
elem.ondrop = (e) => dropHandler(e)