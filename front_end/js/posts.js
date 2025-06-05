const apiServerUrl = 'http://51.44.211.227:5000';
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
                    </div>`;
                return;
            }
            
            const row = document.createElement('div');
            row.className = 'row tm-row';
            postsContainer.appendChild(row);
            
            posts.forEach(post => {
                const date = new Date(post.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });
                
                const postElement = document.createElement('div');
                postElement.className = 'col-12 col-md-6 tm-post';
                postElement.innerHTML = `
                    <hr class="tm-hr-primary">
                    <a href="post.html?post_id=${post.id}" class="effect-lily tm-post-link tm-pt-60">
                        <div class="tm-post-link-inner">
                            ${post.image_url ? `<img src="${post.image_url}" alt="${post.title}" class="img-fluid">` : ''}
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
                    </div>`;
                row.appendChild(postElement);
            });
            
            pageInfo.textContent = `Page ${currentPage}`;
            prevBtn.disabled = currentPage === 1;
        })
        .catch(error => {
            console.error('Error loading posts:', error);
            postsContainer.innerHTML = `
                <div class="col-12 text-center">
                    <p>Error loading posts: ${error.message}</p>
                </div>`;
        });
}

prevBtn.addEventListener('click', () => currentPage > 1 && (currentPage--, loadPosts()));
nextBtn.addEventListener('click', () => (currentPage++, loadPosts()));

loadPosts();
