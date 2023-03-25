// Function that is responsible for displaying form for replying to added comments

function commentReplyToggle(parent_id) {
  const row = document.getElementById(parent_id);
  if (row.classList.contains("hidden")) {
    row.classList.remove("hidden");
  } else {
    row.classList.add("hidden");
  }
}

// POST Request

let csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
const slugUrl = document.querySelector(".slugified-url");

const request = new Request(`/${slugUrl.innerHTML}/`, {
  method: "POST",
  headers: { "X-CSRFToken": csrftoken },
  mode: "same-origin",
});

// Like button functionality

let likeBtn = document.querySelector(".like-btn");
let likeCountNum = document.querySelector(".like-count-num");
const likeForm = document.querySelector(".like-form");

likeForm.addEventListener("submit", (event) => {
  event.preventDefault();

  fetch(request)
    .then((response) => response.text())
    .then((html) => {
      let parser = new DOMParser();
      parser.parseFromString(html, "text/html");

      if (likeBtn.innerHTML === "Like") {
        likeCountNum.innerHTML = parseInt(likeCountNum.innerHTML) + 1;
        likeBtn.innerHTML = "Dislike";
      } else {
        likeCountNum.innerHTML = parseInt(likeCountNum.innerHTML) - 1;
        likeBtn.innerHTML = "Like";
      }
    })
    .catch((error) => {
      console.error("Error ocurred:", error);
    });
});

// Comment form functionality

const commentForm = document.querySelector("#comment-form");
const commentSection = document.querySelector("#comments-section");

function htmlContent(commentDate, currentUser, commentContent, commentId) {
  const htmlComment = `
  <div>
    <hr>
    <div>
        <span class="font-bold">${currentUser}</span>
        <span>${commentDate}</span>
    </div>

    <div class="my-2">
      ${commentContent}
    </div>


    <div class="pt-2 pb-6">
        <a href="/edit-comment/${commentId}"
            class="py-2 px-3 rounded-md text-stone-50 justify-center items-center cursor-pointer bg-neutral-900 hover:bg-neutral-800">
            Edit
        </a>

        <a href="/delete-comment/${commentId}"
            class="py-2 px-3 ml-2 rounded-md text-stone-50 justify-center items-center cursor-pointer bg-neutral-900 hover:bg-neutral-800">
            Delete
        </a>
    </div>
  </div>`;

  return htmlComment;
}

commentForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const form = new FormData(commentForm);

  fetch(`/${slugUrl.innerHTML}/`, {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: form,
  })
    .then((response) => response.text())
    .then((html) => {
      const parser = new DOMParser();
      const parsedDoc = parser.parseFromString(html, "text/html");

      const time = new Date();
      const commentDate = time.toLocaleString("en-US", {
        month: "long",
        day: "numeric",
        year: "numeric",
        hour: "numeric",
        minute: "numeric",
        hour12: true,
      });

      const commentContent = form.get("body");
      const currentUser = document.querySelector(
        "#request-user-comment-form"
      ).textContent;
      const commentId = parsedDoc.querySelector("#parent-comment-id").value;

      const htmlComment = htmlContent(
        commentDate,
        currentUser,
        commentContent,
        commentId
      );

      commentSection.insertAdjacentHTML("afterbegin", htmlComment);
      commentForm.reset();
    })
    .catch((error) => console.error(error));
});
