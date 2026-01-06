/**
 * Book Status Management JavaScript
 * Handles star ratings, reading progress, and user notes
 */

$(document).ready(function() {
    const bookId = getBookIdFromUrl();
    
    if (!bookId) {
        console.error('Could not determine book ID from URL');
        return;
    }
    
    // Initialize star rating clicks
    initializeStarRating();
    
    // Initialize reading progress changes
    initializeReadingProgress();
    
    // Initialize save button
    $('#save-status-btn').click(function() {
        saveBookStatus(bookId);
    });
    
    // Initialize reset button
    $('#reset-status-btn').click(function() {
        resetBookStatus();
    });
});

/**
 * Get book ID from the current URL
 */
function getBookIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    // URL format: /books/<book_id>
    const booksIndex = pathParts.indexOf('books');
    if (booksIndex !== -1 && booksIndex + 1 < pathParts.length) {
        return pathParts[booksIndex + 1];
    }
    return null;
}

/**
 * Initialize star rating functionality
 */
function initializeStarRating() {
    const stars = $('#star-rating-display .star-icon');
    
    stars.on('click', function() {
        const rating = $(this).data('rating');
        updateStarDisplay(rating);
    });
    
    stars.on('mouseenter', function() {
        const rating = $(this).data('rating');
        highlightStars(rating);
    });
    
    $('#star-rating-display').on('mouseleave', function() {
        const currentRating = parseInt($('#rating-value').text());
        updateStarDisplay(currentRating);
    });
}

/**
 * Update star display based on rating
 */
function updateStarDisplay(rating) {
    const stars = $('#star-rating-display .star-icon');
    stars.each(function() {
        const starRating = $(this).data('rating');
        if (starRating <= rating) {
            $(this).removeClass('text-muted').addClass('text-warning');
        } else {
            $(this).removeClass('text-warning').addClass('text-muted');
        }
    });
    $('#rating-value').text(rating + '/5');
}

/**
 * Highlight stars on hover
 */
function highlightStars(rating) {
    const stars = $('#star-rating-display .star-icon');
    stars.each(function() {
        const starRating = $(this).data('rating');
        if (starRating <= rating) {
            $(this).addClass('text-warning');
        } else {
            $(this).removeClass('text-warning');
        }
    });
}

/**
 * Initialize reading progress functionality
 */
function initializeReadingProgress() {
    $('input[name="reading-progress"]').on('change', function() {
        const progress = $(this).val();
        console.log('Reading progress changed to:', progress + '%');
    });
}

/**
 * Save book status to the server
 */
function saveBookStatus(bookId) {
    const starRating = parseInt($('#rating-value').text());
    const readingProgress = $('input[name="reading-progress"]:checked').val();
    const userDescription = $('#user-description').val();
    
    const btn = $('#save-status-btn');
    const originalText = btn.html();
    btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-1"></i> Saving...');
    
    $.ajax({
        url: `/api/books/${bookId}/status`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({
            star_rating: starRating,
            reading_progress: parseInt(readingProgress),
            user_description: userDescription
        }),
        success: function(response) {
            if (response.success) {
                showSuccess('Book status saved successfully!');
            } else {
                showError('Failed to save book status: ' + (response.error || 'Unknown error'));
            }
        },
        error: function(xhr, status, error) {
            showError('Error saving book status: ' + error);
        },
        complete: function() {
            btn.prop('disabled', false).html(originalText);
        }
    });
}

/**
 * Reset book status to original values
 */
function resetBookStatus() {
    // Reload the page to reset all values
    location.reload();
}

/**
 * Show success message
 */
function showSuccess(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $('#book-status-card').prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow', function() {
            $(this).remove();
        });
    }, 5000);
}

/**
 * Show error message
 */
function showError(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    $('#book-status-card').prepend(alertHtml);
}
