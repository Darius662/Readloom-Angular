/**
 * Book Library Filters and Sorting
 * Handles rating filter, sorting by rating, and dynamic filtering
 */

$(document).ready(function() {
    // Initialize filter handlers
    initializeRatingFilter();
    initializeProgressFilter();
    initializeSortingOptions();
});

/**
 * Initialize rating filter
 */
function initializeRatingFilter() {
    $('#bookRatingFilter').on('change', function() {
        const selectedRating = $(this).val();
        filterBooksByRating(selectedRating);
    });
}

/**
 * Initialize progress filter
 */
function initializeProgressFilter() {
    $('#bookProgressFilter').on('change', function() {
        const selectedProgress = $(this).val();
        filterBooksByProgress(selectedProgress);
    });
}

/**
 * Initialize sorting options
 */
function initializeSortingOptions() {
    $('#bookSortBy').on('change', function() {
        const sortBy = $(this).val();
        sortBooks(sortBy);
    });
}

/**
 * Filter books by rating
 */
function filterBooksByRating(minRating) {
    const bookCards = $('#recentBooksGrid .col');
    
    bookCards.each(function() {
        const card = $(this);
        const ratingText = card.find('.star-rating-display').text();
        
        if (minRating === '') {
            // Show all
            card.show();
        } else if (minRating === '0') {
            // Show unrated only
            const hasRating = card.find('.star-rating-display').length > 0;
            if (!hasRating) {
                card.show();
            } else {
                card.hide();
            }
        } else {
            // Show books with rating >= minRating
            const ratingMatch = ratingText.match(/\((\d+)\/5\)/);
            if (ratingMatch) {
                const bookRating = parseInt(ratingMatch[1]);
                if (bookRating >= parseInt(minRating)) {
                    card.show();
                } else {
                    card.hide();
                }
            } else {
                card.hide();
            }
        }
    });
    
    // Show empty state if all books are hidden
    updateEmptyState();
}

/**
 * Filter books by reading progress
 */
function filterBooksByProgress(minProgress) {
    const bookCards = $('#recentBooksGrid .col');
    
    bookCards.each(function() {
        const card = $(this);
        // Get progress from the progress bar floating island (the inner progress div)
        const progressBar = card.find('div[style*="background: linear-gradient"]');
        
        if (minProgress === '') {
            // Show all
            card.show();
        } else if (minProgress === '0') {
            // Show not started only (no progress bar)
            if (progressBar.length === 0) {
                card.show();
            } else {
                card.hide();
            }
        } else {
            // Show books with progress >= minProgress
            if (progressBar.length > 0) {
                const widthStyle = progressBar.attr('style');
                const match = widthStyle.match(/width:\s*(\d+)%/);
                if (match) {
                    const bookProgress = parseInt(match[1]);
                    if (bookProgress >= parseInt(minProgress)) {
                        card.show();
                    } else {
                        card.hide();
                    }
                } else {
                    card.hide();
                }
            } else {
                card.hide();
            }
        }
    });
    
    // Show empty state if all books are hidden
    updateEmptyState();
}

/**
 * Sort books by specified criteria
 */
function sortBooks(sortBy) {
    const grid = $('#recentBooksGrid');
    const bookCards = grid.find('.col').get();
    
    bookCards.sort(function(a, b) {
        const cardA = $(a);
        const cardB = $(b);
        
        switch(sortBy) {
            case 'author':
                return compareText(
                    cardA.find('.card-text.text-muted').eq(0).text(),
                    cardB.find('.card-text.text-muted').eq(0).text()
                );
            
            case 'title':
                return compareText(
                    cardA.find('.card-title').text(),
                    cardB.find('.card-title').text()
                );
            
            case 'rating':
                return compareRating(cardA, cardB);
            
            case 'progress':
                return compareProgress(cardA, cardB);
            
            case 'release_date':
                // If release_date data is available in cards, use it
                return 0; // Placeholder
            
            case 'library':
                // If library data is available in cards, use it
                return 0; // Placeholder
            
            default:
                return 0;
        }
    });
    
    // Re-append sorted cards
    $.each(bookCards, function(index, element) {
        grid.append(element);
    });
}

/**
 * Compare text values (case-insensitive)
 */
function compareText(textA, textB) {
    const a = textA.toLowerCase().trim();
    const b = textB.toLowerCase().trim();
    return a.localeCompare(b);
}

/**
 * Compare ratings (descending order - highest first)
 */
function compareRating(cardA, cardB) {
    const getRating = function(card) {
        const ratingText = card.find('.star-rating-display').text();
        const match = ratingText.match(/\((\d+)\/5\)/);
        return match ? parseInt(match[1]) : 0;
    };
    
    const ratingA = getRating(cardA);
    const ratingB = getRating(cardB);
    
    // Descending order (highest rating first)
    return ratingB - ratingA;
}

/**
 * Compare reading progress (descending order - highest first)
 */
function compareProgress(cardA, cardB) {
    const getProgress = function(card) {
        const progressBar = card.find('div[style*="background: linear-gradient"]');
        if (progressBar.length > 0) {
            const widthStyle = progressBar.attr('style');
            const match = widthStyle.match(/width:\s*(\d+)%/);
            return match ? parseInt(match[1]) : 0;
        }
        return 0;
    };
    
    const progressA = getProgress(cardA);
    const progressB = getProgress(cardB);
    
    // Descending order (highest progress first)
    return progressB - progressA;
}

/**
 * Update empty state message
 */
function updateEmptyState() {
    const visibleCards = $('#recentBooksGrid .col:visible').length;
    
    if (visibleCards === 0) {
        if ($('#recentBooksGrid .empty-state').length === 0) {
            $('#recentBooksGrid').html(`
                <div class="col-12 text-center py-4 empty-state">
                    <i class="fas fa-filter fa-3x text-muted mb-3"></i>
                    <p>No books match your filter criteria</p>
                </div>
            `);
        }
    } else {
        $('#recentBooksGrid .empty-state').remove();
    }
}
