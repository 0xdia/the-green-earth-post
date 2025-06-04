// @TODO: API URL
const apiServerUrl = 'http://35.180.97.192:5000';

let currentPage = 1;
const postsPerPage = 5;

const postsContainer = document.getElementById('posts-container');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');
const pageInfo = document.getElementById('page-info');

function loadPosts() {
    const offset = (currentPage - 1) * postsPerPage;
    
    axios.get(`${apiServerUrl}/api/posts?limit=${postsPerPage}&offset=${offset}`)
        .then(response => {
            const posts = response.data;
            postsContainer.innerHTML = '';
            
            if (posts.length === 0) {
                postsContainer.innerHTML = `
                    <div class="col-12 text-center">
                        <p>No posts yet. Be the first to create one!</p>
                        <a href="create-post.html" class="tm-btn tm-btn-primary">Create Post</a>
                    </div>
                `;
                return;
            }
            
            posts.forEach(post => {
                const date = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                let imageHtml = '';
                if (post.image_url) {
                    imageHtml = `<img src="${post.image_url}" alt="${post.title}" class="img-fluid">`;
                }
                
                const postHtml = `
                    <article class="col-12 col-md-6 tm-post">
                        <hr class="tm-hr-primary">
                        <a href="post.html?post_id=${post.id}" class="effect-lily tm-post-link tm-pt-60">
                            <div class="tm-post-link-inner">
                                ${imageHtml}
                            </div>
                            <h2 class="tm-pt-30 tm-color-primary tm-post-title">${post.title}</h2>
                        </a>                    
                        <p class="tm-pt-30">
                            ${post.content.substring(0, 150)}...
                        </p>
                        <div class="d-flex justify-content-between tm-pt-45">
                            <span class="tm-color-primary">${post.category}</span>
                            <span class="tm-color-primary">${date}</span>
                        </div>
                        <hr>
                        <div class="d-flex justify-content-between">
                            <span>${post.author || 'Anonymous'}</span>
                            <a href="post.html?post_id=${post.id}" class="tm-color-primary">Read more</a>
                        </div>
                    </article>
                `;
                
                postsContainer.innerHTML += postHtml;
            });
            
            // Update pagination controls
            pageInfo.textContent = `Page ${currentPage}`;
            prevBtn.disabled = currentPage === 1;
        })
        .catch(error => {
            console.error('Error loading posts:', error);
            postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
        });
}

prevBtn.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        loadPosts();
    }
});

nextBtn.addEventListener('click', () => {
    currentPage++;
    loadPosts();
});

loadPosts();
