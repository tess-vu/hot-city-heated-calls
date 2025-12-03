// Wait for DOM to fully load before running script
document.addEventListener("DOMContentLoaded", () => {
    
    const navPanel = document.querySelector(".panel-left-nav");
    const contentMiddle = document.getElementById("content-middle");
    const contentRight = document.getElementById("content-right");

    // Store currently active link
    let activeLink = null;
    // Track if we're on a code page
    let currentPage = null;
    
    // Grain Texture
    function initGrainTexture() {
        const grainOptionsMiddle = {
            animate: true,
            patternWidth: 200,
            patternHeight: 200,
            grainOpacity: 0.25,
            grainDensity: 1,
            grainWidth: 1.1,
            grainHeight: 1.1,
            grainChaos: 0.5,
            grainSpeed: 20
        };

        if (typeof grained !== 'undefined') {
            const grainElement = document.getElementById('grain-middle');
            if (grainElement) {
                grained("#grain-middle", grainOptionsMiddle);
                console.log("Grain texture applied to middle panel.");
            }
        }
    }

    initGrainTexture();

    // Navigation - Event Delegation
    navPanel.addEventListener("click", (e) => {
        const clickedLink = e.target.closest("a");

        if (!clickedLink) {
            return;
        }

        // Check if this is just the CODE toggle (no data-page)
        if (clickedLink.classList.contains('submenu-toggle') && !clickedLink.dataset.page) {
            // Don't prevent default or load anything - just let CSS handle the hover
            return;
        }

        e.preventDefault(); 

        const pageName = clickedLink.dataset.page;
        if (!pageName) {
            return;
        }

        // Update active state
        updateActiveState(clickedLink, pageName);

        // Load the content
        loadContent(pageName);
    });

    /**
     * Update active state for navigation
     */
    function updateActiveState(clickedLink, pageName) {
        // Remove active from previous
        if (activeLink) {
            activeLink.classList.remove("active");
        }
        
        // Check if this is a notebook page (starts with "04")
        const isNotebookPage = pageName.startsWith('04');
        
        if (isNotebookPage) {
            // For notebook pages, activate the specific submenu item
            // and also highlight the CODE parent
            activeLink = clickedLink;
            activeLink.classList.add("active");
            
            // Keep the submenu expanded by adding a class to parent
            const submenuParent = navPanel.querySelector('.has-submenu');
            if (submenuParent) {
                submenuParent.classList.add('submenu-active');
            }
        } else {
            // Regular page
            activeLink = clickedLink;
            activeLink.classList.add("active");
            
            // Remove submenu-active when navigating away from code
            const submenuParent = navPanel.querySelector('.has-submenu');
            if (submenuParent) {
                submenuParent.classList.remove('submenu-active');
            }
        }
        
        currentPage = pageName;
    }

    /**
     * Fetch and load page content
     */
    async function loadContent(pageName) {
        contentMiddle.innerHTML = `<p>Loading...</p>`;
        contentRight.innerHTML = "";

        try {
            const response = await fetch(`pages/${pageName}.html`);

            if (!response.ok) {
                throw new Error(`Could not load page: ${response.status}`);
            }

            const fragmentText = await response.text();

            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = fragmentText;

            const middleFragment = tempDiv.querySelector('.content-middle');
            const rightFragment = tempDiv.querySelector('.content-right');

            contentMiddle.innerHTML = middleFragment ? 
                middleFragment.innerHTML : 
                `<p>Content for middle panel not found.</p>`;
            
            contentRight.innerHTML = rightFragment ? 
                rightFragment.innerHTML : 
                '';

            // Scroll to top
            contentMiddle.scrollTop = 0;
            contentRight.scrollTop = 0;

            // Attach click handlers to any navigation links in the loaded content
            attachContentNavHandlers();

        } catch (error) {
            console.error("Fetch Error:", error);
            contentMiddle.innerHTML = `<p class="error">Error loading content. Please check the file path and console.</p>`;
        }
    }

    /**
     * Attach click handlers to navigation links within loaded content
     * (for prev/next buttons and right panel notebook list)
     */
    function attachContentNavHandlers() {
        // Handle all links with data-page attribute in content areas
        const contentLinks = document.querySelectorAll('#content-middle a[data-page], #content-right a[data-page]');
        
        contentLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const pageName = link.dataset.page;
                if (pageName) {
                    // Find the corresponding nav link to update active state
                    const navLink = navPanel.querySelector(`a[data-page="${pageName}"]`);
                    if (navLink) {
                        updateActiveState(navLink, pageName);
                    }
                    loadContent(pageName);
                }
            });
        });
    }

    // Load introduction page on initial visit
    const initialLink = navPanel.querySelector('a[data-page="01_introduction"]');
    if (initialLink) {
        initialLink.click();
    }

    /**
     * Toggle all code cells in notebook view
     */
    window.toggleAllCode = function(show) {
        const codeBlocks = document.querySelectorAll('.code-fold');
        codeBlocks.forEach(block => {
            if (show) {
                block.setAttribute('open', '');
            } else {
                block.removeAttribute('open');
            }
        });
    };
});