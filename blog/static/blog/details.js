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

function htmlContent(currentUser, commentContent, commentId) {
  const htmlComment = `
      <div class="pt-10">
        <p>
            ${currentUser}
            <span> {{ comment.created_on }} </span>
        </p>

        ${commentContent}

        <div class="py-4">
          <a href="/edit-comment/${commentId}"
            class="mr-1 inline-flex items-center justify-center px-4 py-2 text-base font-medium leading-6 text-gray-600 whitespace-no-wrap bg-white border border-gray-200 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:shadow-none">
            Edit
          </a>
          <a href="/delete-comment/${commentId}"
            class="ml-1 inline-flex items-center justify-center px-4 py-2 text-base font-medium leading-6 text-gray-600 whitespace-no-wrap bg-white border border-gray-200 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:shadow-none">
            Delete
          </a>

          <button onclick="commentReplyToggle('${commentId}')" type="submit"
              class="inline-flex items-center justify-center px-4 py-2 text-base font-medium leading-6 text-gray-600 whitespace-no-wrap bg-white border border-gray-200 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:shadow-none"
              data-parent-id="${commentId}">Reply</button>
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

      const commentContent = form.get("body");
      const currentUser = document.querySelector(
        "#request-user-comment-form"
      ).textContent;
      const commentId = parsedDoc.querySelector("#parent-comment-id").value;

      const htmlComment = htmlContent(currentUser, commentContent, commentId);

      commentSection.insertAdjacentHTML("afterbegin", htmlComment);
      commentForm.reset();
    })
    .catch((error) => console.error(error));
});
