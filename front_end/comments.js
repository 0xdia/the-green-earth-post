// @TODO: API URL
const apiServerUrl = 'http://51.44.218.150:5000';

// Get post ID from URL for single post pages
function getPostId() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('post_id');
}

// Post comment function
function postComment() {
    const nameInput = document.getElementById("name");
    const messageInput = document.getElementById("message");
    const btn = document.getElementById("post-comment");
    
    if (!nameInput || !messageInput || !btn) return;

    btn.addEventListener("click", () => {
        const name = nameInput.value;
        const message = messageInput.value;
        const date = (new Date()).toDateString();
        const postId = getPostId();

        if (!postId) {
            alert('Post ID is missing');
            return;
        }

        if (name === '' || message === '') {
            alert('Name or message is missing');
            return;
        }

        const json = JSON.stringify({
            post_id: postId,
            name: name,
            comment: message,
            date: date
        });
        
        axios.post(apiServerUrl + "/api/comment", json, {
            headers: { 'Content-Type': 'application/json' }
        })
        .then(() => {
            alert('Your message has been sent!');
            nameInput.value = '';
            messageInput.value = '';
            getComments();
        })
        .catch(err => {
            console.error(err);
            alert('Failed to post comment. Please try again.');
        });
    });
}

// Get comments function
function getComments() {
    const postId = getPostId();
    if (!postId) return;

    axios.get(apiServerUrl + "/api/comments/" + postId)
        .then(response => {
            const commentsContainer = document.getElementById("get-comments");
            if (!commentsContainer) return;
            
            commentsContainer.innerHTML = '';
            
            response.data.forEach(comment => {
                commentsContainer.innerHTML += getCommentHtml(
                    comment.name, 
                    comment.comment, 
                    comment.date
                );
            });
        })
        .catch(err => console.error(err));
}

// Generate comment HTML
function getCommentHtml(name, comment, date) {
    return `
        <div class="tm-comment tm-mb-45">
            <figure class="tm-comment-figure">
                <img src="img/comment.png" alt="Image" class="mb-2 rounded-circle img-thumbnail">
                <figcaption class="tm-color-primary text-center">${name}</figcaption>
            </figure>
            <div>
                <p>${comment}</p>
                <div class="d-flex justify-content-between">
                    <span class="tm-color-primary">${new Date(date).toLocaleDateString()}</span>
                </div>
            </div>
        </div>
    `;
}

// Initialize
if (document.getElementById("post-comment")) {
    postComment();
}

if (document.getElementById("get-comments")) {
    getComments();
}
