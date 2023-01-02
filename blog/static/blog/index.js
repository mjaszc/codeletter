let csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
let likeBtn = document.querySelector('.like-btn');
let likeCountNum = document.querySelector('.like-count-num');
const likeForm = document.querySelector('.like-form');
const slugUrl = document.querySelector('.slugified-url');

const notificationSocket = new WebSocket(`ws://${window.location.host}/ws/notification/`);

notificationSocket.onmessage = (e) => {
    let data = JSON.parse(e.data)
        console.log(data.message);
}

notificationSocket.onclose = function(){
    console.error("Socket close unexpectedly");
}

likeBtn.onclick = function(){
    const message = "websocket is working correctly.";
    notificationSocket.send(JSON.stringify({'message': message}))
}


const request = new Request(
    `/${slugUrl.innerHTML}/`,
    {
        method: 'POST',
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin',
    }
);


likeForm.addEventListener("submit", event => {
    event.preventDefault();

    fetch(request)
        .then(response => response.text())
        .then(html => {
            let parser = new DOMParser();
            let data = parser.parseFromString(html, 'text/html');
            console.log("Success", data);

            if(likeBtn.innerHTML === "Like") {
                likeCountNum.innerHTML = parseInt(likeCountNum.innerHTML) + 1;
                likeBtn.innerHTML = "Dislike";
            } else {
                likeCountNum.innerHTML = parseInt(likeCountNum.innerHTML) - 1;
                likeBtn.innerHTML = "Like";
            };
        })
        .catch(error => {
        console.error('Error ocurred:', error);
        });

})
