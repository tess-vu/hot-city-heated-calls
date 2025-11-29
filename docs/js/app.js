/* js/app.js */

// Wait for DOM to fully load before running script
document.addEventListener("DOMContentLoaded", () => {
    
    const navPanel = document.querySelector(".panel-left-nav");
    const contentMiddle = document.getElementById("content-middle");
    const contentRight = document.getElementById("content-right");

    // Store currently active link
    let activeLink = null;
    
    // Grain Texture
    function initGrainTexture() {
        // Grain options
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

        // Apply grain to middle panel overlay
        if (typeof grained !== 'undefined') {
            const grainElement = document.getElementById('grain-middle');
            if (grainElement) {
                grained("#grain-middle", grainOptionsMiddle);
                console.log("✓ Grain texture applied to middle panel");
            } else {
                console.error("Grain element #grain-middle not found in DOM");
            }
        } else {
            console.error("Grained library not loaded. Make sure the script is included in index.html");
        }
    }

    // Initialize grain texture once
    initGrainTexture();

    // Navigation and Content Loading
    // Event Delegation: Listen for clicks on entire nav panel
    navPanel.addEventListener("click", (e) => {
        // Find the <a> tag that was clicked
        const clickedLink = e.target.closest("a");

        if (!clickedLink) {
            return; // Click wasn't on a link
        }

        // Prevent page reload
        e.preventDefault(); 

        const pageName = clickedLink.dataset.page;
        if (!pageName) {
            console.error("Link is missing data-page attribute.");
            return;
        }

        // Manage Active State
        if (activeLink) {
            activeLink.classList.remove("active");
        }
        activeLink = clickedLink;
        activeLink.classList.add("active");

        // Load the content
        loadContent(pageName);
    });

    /**
     * Fetch content fragment from /pages/ directory
     * and inject into middle and right panels.
     * 
     * Replace innerHTML of content-middle
     * Grain overlay (#grain-middle) is positioned with fixed,
     * so it's not affected by content changes.
     */
    async function loadContent(pageName) {
        // Set loading state
        contentMiddle.innerHTML = `<p>Loading...</p>`;
        contentRight.innerHTML = "";

        try {
            const response = await fetch(`pages/${pageName}.html`);

            if (!response.ok) {
                throw new Error(`Could not load page: ${response.status}`);
            }

            const fragmentText = await response.text();

            // Parse the fetched HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = fragmentText;

            // Find content for each panel
            const middleFragment = tempDiv.querySelector('.content-middle');
            const rightFragment = tempDiv.querySelector('.content-right');

            // Inject content directly
            // (Grain overlay is separate, so this won't affect it)
            contentMiddle.innerHTML = middleFragment ? 
                middleFragment.innerHTML : 
                `<p>Content for middle panel not found.</p>`;
            
            contentRight.innerHTML = rightFragment ? 
                rightFragment.innerHTML : 
                '';

            // Scroll panels back to top
            contentMiddle.scrollTop = 0;
            contentRight.scrollTop = 0;

        } catch (error) {
            console.error("Fetch Error:", error);
            contentMiddle.innerHTML = `<p class="error">Error loading content. Please check the file path and console.</p>`;
        }
    }

    // Load introduction page on initial visit
    const initialLink = navPanel.querySelector('a[data-page="01_introduction"]');
    if (initialLink) {
        initialLink.click();
    }
});