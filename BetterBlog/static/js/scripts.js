/**
 * Event listener for the scroll behavior
 * When the user scrolls, this function is called to handle the scroll behavior and update the navigation bar.
 */
window.addEventListener('DOMContentLoaded', () => {
    let scrollPos = 0; // Stores the previous scroll position
    const mainNav = document.getElementById('mainNav'); // Reference to the main navigation element
    const headerHeight = mainNav.clientHeight; // Height of the header

    /**
     * Event listener for scroll events
     * Updates the visibility and positioning of the main navigation element based on scroll behavior.
     */
    window.addEventListener('scroll', function () {
        const currentTop = document.body.getBoundingClientRect().top * -1; // Current distance from the top of the document
        if (currentTop < scrollPos) {
            // Scrolling Up
            if (currentTop > 0 && mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-visible');
            } else {
                console.log(123);
                mainNav.classList.remove('is-visible', 'is-fixed');
            }
        } else {
            // Scrolling Down
            mainNav.classList.remove(['is-visible']);
            if (currentTop > headerHeight && !mainNav.classList.contains('is-fixed')) {
                mainNav.classList.add('is-fixed');
            }
        }
        scrollPos = currentTop; // Update the previous scroll position
    });
});


/**
 * Handles the like button functionality
 * Updates the like count and style of the like button for a specific post.
 *
 * @param {string} postId - The ID of the post to perform the like action on.
 */
function like(postId) {
    const likeCount = document.getElementById(`likes-count-${postId}`); // Reference to the element displaying the like count
    const likeButton = document.getElementById(`like-button-${postId}`); // Reference to the like button element

    // Send a GET request to the specified URL to perform the like action
    fetch(`/like-post/${postId}`, {method: 'GET'})
        .then((res) => res.json()) // Wait for the response and parse it as JSON
        .then((data) => {
            likeCount.innerHTML = data['likes']; // Update the like count with the returned value
            console.log(data);
            if (data['liked'] === true) {
                likeButton.className = 'fa-solid fa-thumbs-up fa-2x'; // Add the "fa-solid" class to show a filled thumbs-up icon
            } else {
                likeButton.className = 'fa-regular fa-thumbs-up fa-2x'; // Add the "fa-regular" class to show an outlined thumbs-up icon
            }
        })
        .catch((e) => console.log(e)); // Log any errors that occur during the fetch request
}


// Add an event listener to the "Add comment here" button
document.getElementById("addComment").addEventListener("click", function () {
    document.getElementById("commentDiv").style.display = "block";
    document.getElementById("addComment").style.display = "none";
});


function appendComment(author, content, date) {
    const commentsList = document.querySelector('.comments-list');

    // Create a new comment element
    const newComment = document.createElement('div');
    newComment.classList.add('comment-box');
    newComment.innerHTML = `
        <div class="comment">
            <div class="comment-header">
                <a class="comment-author" href="#">${author}</a>
            </div>
            <a class="comment-delete">
                 Refresh page to use Delete
            </a>
            <div class="comment-content">
                ${content}
            </div>
            <div class="comment-date">
                <small class="text-muted">${date}</small>
            </div>
        </div>
    `;

    // Append the new comment to the comments list
    commentsList.appendChild(newComment);
}


function addComment(postId) {
    const commentInput = document.querySelector('#commentForm textarea');
    const commentContent = commentInput.value;

    if (!commentContent.trim()) {
        return; // Skip empty comments
    }

    const formData = {
        body: commentContent
    };

    // Send a POST request to the add_comment route with the comment data
    fetch(`/post/${postId}/add_comment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            // Handle the JSON response data
            console.log(data);

            if (data.message === 'Comment added successfully') {
                // Append the new comment to the comments section
                appendComment(data.comment.author, data.comment.content, data.comment.date);
                // Reset the comment input field
                commentInput.value = '';
            } else {
                // Display an error message if the comment was not added successfully
                console.log('Error:', data.message);
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
}

function deleteComment(commentId, postId) {
    fetch(`/delete/${commentId}/${postId}`, {
        method: 'DELETE',
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.message === 'Comment deleted successfully') {
                const commentElement = document.getElementById(`commentID-${commentId}`);
                if (commentElement) {
                    commentElement.remove();
                }
            } else {
                console.log('Error:', data.message);
            }
        })
        .catch(error => {
            console.log('Error:', error);
        });
}











