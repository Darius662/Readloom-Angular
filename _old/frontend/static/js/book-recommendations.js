/**
 * Book Recommendations Module
 * Handles loading and displaying category-based book recommendations
 */

// Store recommendations data globally
window.recommendationsData = {};

$(document).ready(function() {
    // Get book ID from the URL
    const bookId = getBookIdFromUrl();
    if (bookId) {
        loadCategoryRecommendations(bookId);
    }
    
    // Attach event handler for book details buttons
    $(document).on('click', '.book-details-btn', function() {
        const bookIndex = $(this).data('book-index');
        const book = window.recommendationsData[bookIndex];
        if (book) {
            showBookDetailsModal(book);
        }
    });
    
    // Attach handler for add to collection button (for recommended books)
    $(document).on('click', '#btnAddToCollection', function(e) {
        const recommendedBook = $(this).data('recommended-book');
        if (recommendedBook) {
            e.preventDefault();
            handleAddRecommendedToCollection();
        }
    });
});

/**
 * Extract book ID from the current URL
 */
function getBookIdFromUrl() {
    const pathParts = window.location.pathname.split('/');
    const booksIndex = pathParts.indexOf('books');
    if (booksIndex !== -1 && booksIndex + 1 < pathParts.length) {
        return parseInt(pathParts[booksIndex + 1]);
    }
    return null;
}

/**
 * Load AI-powered recommendations for the current book
 * Falls back to category-only if AI fails
 */
function loadCategoryRecommendations(bookId) {
    $.ajax({
        url: `/api/books/${bookId}/recommendations/ai`,
        type: 'GET',
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                displayRecommendations(response.data.recommendations, response.data.method);
            } else {
                showEmptyRecommendations('Failed to load recommendations');
            }
        },
        error: function(xhr, status, error) {
            console.error('Error loading recommendations:', error);
            showEmptyRecommendations('Unable to load recommendations');
        }
    });
}

/**
 * Display recommendations in the UI
 */
function displayRecommendations(recommendations, method) {
    const container = $('#recommendations-container');
    
    if (!recommendations || recommendations.length === 0) {
        const message = method === 'ai' 
            ? 'No AI recommendations available. Try category-based recommendations instead.'
            : 'No recommendations available for this book.';
        
        container.html(`
        <div class="col-12">
            <div class="text-center text-muted py-4">
                <i class="fas fa-info-circle me-2"></i>
                ${message}
            </div>
        </div>
    `);
        return;
    }
    
    // Clear previous recommendations data
    window.recommendationsData = {};
    
    // Build HTML for recommendations using the same layout as the Books tab
    let html = '';
    recommendations.forEach((book, index) => {
        // Store book data for modal
        window.recommendationsData[index] = book;
        
        const title = book.title || 'Unknown Title';
        const author = book.author || 'Unknown Author';
        const coverUrl = book.cover_url || '/static/img/no-cover.png';
        
        // Truncate title if too long
        const displayTitle = title.length > 30 ? title.substring(0, 27) + '...' : title;
        
        html += `
        <div class="col">
            <div class="card h-100 d-flex flex-column">
                <!-- Book Cover -->
                <div style="position: relative; overflow: hidden; flex-shrink: 0;">
                    <img src="${coverUrl}" class="card-img-top book-cover" alt="${title}" style="width: 100%; height: auto; aspect-ratio: 2/3; object-fit: cover; cursor: pointer; display: block;">
                </div>
                <div class="card-body py-2 px-2 flex-grow-1 d-flex flex-column">
                    <h6 class="card-title mb-1" title="${title}" style="font-size: 0.85rem; line-height: 1.2;">${displayTitle}</h6>
                    <p class="card-text text-muted mb-0" title="${author}" style="font-size: 0.75rem;">${author}</p>
                </div>
                <div class="card-footer p-1">
                    <button class="btn btn-primary btn-sm w-100 book-details-btn" data-book-index="${index}" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">
                        <i class="fas fa-book-open me-1" style="font-size: 0.65rem;"></i> Details
                    </button>
                </div>
            </div>
        </div>
        `;
    });
    
    // Use the same grid layout as the Books tab
    container.html(`<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 row-cols-xl-5 row-cols-xxl-6 g-4">${html}</div>`);
}

/**
 * Generate star rating HTML
 */
function generateStarRating(rating) {
    let html = '';
    for (let i = 0; i < 5; i++) {
        if (i < rating) {
            html += '<i class="fas fa-star text-warning" style="font-size: 0.8rem;"></i>';
        } else {
            html += '<i class="fas fa-star text-muted" style="font-size: 0.8rem;"></i>';
        }
    }
    return html;
}

/**
 * Show empty state message
 */
function showEmptyRecommendations(message) {
    const container = $('#recommendations-container');
    container.html(`
        <div class="col-12">
            <div class="text-center text-muted py-4">
                <i class="fas fa-info-circle me-2"></i>
                ${message}
            </div>
        </div>
    `);
}

/**
 * Show book details in a modal (using the existing bookDetailsModal from search.html)
 */
function showBookDetailsModal(book) {
    // Check if modal exists, if not create it
    if ($('#bookDetailsModal').length === 0) {
        createBookDetailsModal();
    }
    
    // Log the book data for debugging
    console.log('Showing book details:', book);
    
    // Update modal title
    $('#bookDetailsModalLabel').text('Book Details');
    
    // Reset modal with loading state
    $('#modalTitle').text('Loading...');
    $('#modalCover').attr('src', '/static/img/no-cover.png');
    $('#modalAltTitles').empty();
    $('#modalAuthor').text('');
    $('#modalPublisher').text('');
    $('#modalPublishedDate').text('');
    $('#modalISBN').text('');
    $('#modalGenres').empty();
    $('#modalDescription').text('Loading...');
    
    // Store book data for add to collection
    $('#btnAddToCollection').data('recommended-book', book);
    
    // Ensure collections are loaded
    loadCollectionsForModal();
    
    // Show modal
    const bookModal = new bootstrap.Modal(document.getElementById('bookDetailsModal'));
    bookModal.show();
    
    // Fetch full book details from metadata API
    const source = book.metadata_source || book.provider;
    const id = book.metadata_id || book.id;
    
    if (source && id) {
        const apiUrl = `/api/metadata/manga/${source}/${id}`;
        console.log('Fetching book details from:', apiUrl);
        console.log('Book data:', book);
        console.log('Using source:', source, 'id:', id);
        
        $.ajax({
            url: apiUrl,
            method: 'GET',
            success: function(data) {
                console.log('Metadata API response:', data);
                // Update modal with book details
                $('#modalTitle').text(data.title || 'Unknown Title');
                
                // Use image proxy for external images in modal
                let modalCoverUrl = data.cover_url || '/static/img/no-cover.png';
                if (modalCoverUrl && modalCoverUrl.startsWith('http')) {
                    modalCoverUrl = `/api/proxy/image?url=${encodeURIComponent(modalCoverUrl)}`;
                }
                $('#modalCover').attr('src', modalCoverUrl);
                
                // Alternative titles
                if (data.alternative_titles && data.alternative_titles.length > 0) {
                    $('#modalAltTitles').text('Also known as: ' + data.alternative_titles.join(', '));
                } else {
                    $('#modalAltTitles').empty();
                }
                
                // Author
                $('#modalAuthor').text(data.author || 'Unknown');
                
                // Publisher
                $('#modalPublisher').text(data.publisher || 'Unknown');
                
                // Published date
                $('#modalPublishedDate').text(data.published_date || 'Unknown');
                
                // ISBN
                $('#modalISBN').text(data.isbn || 'Unknown');
                
                // Genres
                let genresHtml = '';
                if (data.genres && Array.isArray(data.genres) && data.genres.length > 0) {
                    genresHtml = data.genres.map(genre => 
                        `<span class="badge bg-secondary me-1 mb-1">${genre}</span>`
                    ).join('');
                } else if (data.subjects) {
                    // Handle subjects as string or array
                    let subjectsArray = [];
                    if (typeof data.subjects === 'string') {
                        subjectsArray = data.subjects.split(',').map(s => s.trim()).filter(s => s);
                    } else if (Array.isArray(data.subjects)) {
                        subjectsArray = data.subjects;
                    }
                    if (subjectsArray.length > 0) {
                        genresHtml = subjectsArray.map(genre => 
                            `<span class="badge bg-secondary me-1 mb-1">${genre}</span>`
                        ).join('');
                    }
                }
                $('#modalGenres').html(genresHtml || '<span class="text-muted">No genres available</span>');
                
                // Description
                $('#modalDescription').text(data.description || 'No description available');
            },
            error: function(xhr) {
                console.error('Error fetching book details:', xhr.responseText);
                // Fallback to using the data we have
                $('#modalTitle').text(book.title || 'Unknown Title');
                $('#modalAuthor').text(book.author || 'Unknown');
                $('#modalPublisher').text(book.publisher || 'Unknown');
                $('#modalPublishedDate').text(book.published_date || 'Unknown');
                $('#modalISBN').text(book.isbn || 'Unknown');
                
                if (book.subjects && typeof book.subjects === 'string') {
                    const subjectsArray = book.subjects.split(',').map(s => s.trim()).filter(s => s);
                    const genresHtml = subjectsArray.map(genre => 
                        `<span class="badge bg-secondary me-1 mb-1">${genre}</span>`
                    ).join('');
                    $('#modalGenres').html(genresHtml || '<span class="text-muted">No genres available</span>');
                } else {
                    $('#modalGenres').html('<span class="text-muted">No genres available</span>');
                }
                
                $('#modalDescription').text(book.description || 'No description available');
            }
        });
    } else {
        // No metadata source/id, use what we have
        $('#modalTitle').text(book.title || 'Unknown Title');
        $('#modalAuthor').text(book.author || 'Unknown');
        $('#modalPublisher').text(book.publisher || 'Unknown');
        $('#modalPublishedDate').text(book.published_date || 'Unknown');
        $('#modalISBN').text(book.isbn || 'Unknown');
        
        if (book.subjects && typeof book.subjects === 'string') {
            const subjectsArray = book.subjects.split(',').map(s => s.trim()).filter(s => s);
            const genresHtml = subjectsArray.map(genre => 
                `<span class="badge bg-secondary me-1 mb-1">${genre}</span>`
            ).join('');
            $('#modalGenres').html(genresHtml || '<span class="text-muted">No genres available</span>');
        } else {
            $('#modalGenres').html('<span class="text-muted">No genres available</span>');
        }
        
        $('#modalDescription').text(book.description || 'No description available');
    }
}

/**
 * Create the book details modal if it doesn't exist
 */
function createBookDetailsModal() {
    const modalHtml = `
        <div class="modal fade" id="bookDetailsModal" tabindex="-1" aria-labelledby="bookDetailsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="bookDetailsModalLabel">Book Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-4 mb-3">
                                <img id="modalCover" src="" alt="Cover Image" class="img-fluid rounded">
                                <div class="mt-3">
                                    <div class="mb-2">
                                        <label class="form-label small mb-1">Collection</label>
                                        <select id="modalCollection" class="form-select form-select-sm">
                                            <!-- Collections will be populated dynamically -->
                                        </select>
                                    </div>
                                    <div class="mb-3">
                                        <label class="form-label small mb-1">Root Folder</label>
                                        <select id="modalRootFolder" class="form-select form-select-sm">
                                            <option value="">-- Auto --</option>
                                            <!-- Root folders will be populated dynamically -->
                                        </select>
                                    </div>
                                    <button id="btnAddToCollection" class="btn btn-success w-100">
                                        <i class="fas fa-plus-circle me-2"></i> Add to Collection
                                    </button>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <h4 id="modalTitle" class="mb-3"></h4>
                                <div id="modalAltTitles" class="text-muted small mb-3"></div>
                                
                                <!-- Author info will be dynamically populated here -->
                                <div id="modalAuthor" class="mb-4"></div>
                                
                                <!-- Book-specific fields -->
                                <div class="book-fields">
                                    <div class="mb-3">
                                        <strong>Publisher:</strong> <span id="modalPublisher"></span>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <strong>Published:</strong> <span id="modalPublishedDate"></span>
                                    </div>
                                    
                                    <div class="mb-3">
                                        <strong>ISBN:</strong> <span id="modalISBN"></span>
                                    </div>
                                </div>
                                
                                <!-- Genres/Subjects -->
                                <div class="mb-4">
                                    <strong>Subjects:</strong>
                                    <div id="modalGenres" class="mt-2"></div>
                                </div>
                                
                                <!-- Description/Biography -->
                                <div class="mb-3">
                                    <strong>Description:</strong>
                                    <div id="modalDescription" class="mt-2 description-box" style="max-height: 200px; overflow-y: auto; padding: 10px; background-color: rgba(0,0,0,0.1); border-radius: 4px;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalHtml);
}

/**
 * Load collections for the modal dropdown
 */
function loadCollectionsForModal() {
    $.ajax({
        url: '/api/collections?content_type=BOOK',
        type: 'GET',
        dataType: 'json',
        success: function(collections) {
            const select = $('#modalCollection');
            select.empty();
            select.append('<option value="">-- Select Collection --</option>');
            
            if (collections && collections.length > 0) {
                collections.forEach(function(collection) {
                    select.append(`<option value="${collection.id}">${collection.name}</option>`);
                });
            }
        }
    });
}

/**
 * Handle add to collection for recommended books
 */
function handleAddRecommendedToCollection() {
    const book = $('#btnAddToCollection').data('recommended-book');
    
    if (!book) {
        return; // Not a recommended book
    }
    
    const collectionId = $('#modalCollection').val();
    const rootFolderId = $('#modalRootFolder').val() || null;
    
    if (!collectionId) {
        alert('Please select a collection');
        return;
    }
    
    // Disable button and show loading state
    const $btn = $('#btnAddToCollection');
    const originalText = $btn.html();
    $btn.prop('disabled', true).html('<i class="fas fa-spinner fa-spin me-2"></i> Adding...');
    
    // Create book data for adding to collection
    const bookData = {
        title: book.title,
        author: book.author,
        cover_url: book.cover_url,
        description: book.description,
        publisher: book.publisher,
        published_date: book.published_date,
        isbn: book.isbn,
        subjects: book.subjects ? book.subjects.split(',').map(s => s.trim()) : [],
        metadata_source: book.metadata_source,
        metadata_id: book.metadata_id,
        content_type: 'BOOK',
        collection_id: collectionId,
        root_folder_id: rootFolderId
    };
    
    // Call API to create series
    $.ajax({
        url: '/api/series',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(bookData),
        success: function(response) {
            // Reset button
            $btn.prop('disabled', false).html(originalText);
            
            // Close modal
            bootstrap.Modal.getInstance(document.getElementById('bookDetailsModal')).hide();
            
            notificationManager.success('Book added to collection!');
        },
        error: function(xhr) {
            // Reset button
            $btn.prop('disabled', false).html(originalText);
            
            const error = xhr.responseJSON?.error || 'Failed to add book';
            notificationManager.error(error);
        }
    });
}
