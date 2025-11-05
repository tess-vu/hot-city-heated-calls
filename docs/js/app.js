/* js/app.js */

// Wait for the DOM to be fully loaded before running the script
document.addEventListener("DOMContentLoaded", () => {
    
    const navPanel = document.querySelector(".panel-left-nav");
    const contentMiddle = document.getElementById("content-middle");
    const contentRight = document.getElementById("content-right");

    // Store the currently active link
    let activeLink = null;

    // 1. EVENT DELEGATION: Listen for clicks on the entire nav panel
    navPanel.addEventListener("click", (e) => {
        // Find the <a> tag that was clicked, if any
        const clickedLink = e.target.closest("a");

        if (!clickedLink) {
            return; // Click wasn't on a link, do nothing
        }

        // Prevent the link from causing a page reload
        e.preventDefault(); 

        const pageName = clickedLink.dataset.page;
        if (!pageName) {
            console.error("Link is missing data-page attribute.");
            return;
        }

        // 2. Manage Active State
        if (activeLink) {
            activeLink.classList.remove("active");
        }
        activeLink = clickedLink;
        activeLink.classList.add("active");

        // 3. Load the content
        loadContent(pageName);
    });

    /**
     * Fetches a content fragment from the /pages/ directory
     * and injects it into the middle and right panels.
     * [17, 20]
     */
    async function loadContent(pageName) {
        // Set loading state (optional, but good UX)
        contentMiddle.innerHTML = `<p>Loading...</p>`;
        contentRight.innerHTML = "";

        try {
            const response = await fetch(`pages/${pageName}.html`);

            if (!response.ok) {
                throw new Error(`Could not load page: ${response.status}`);
            }

            const fragmentText = await response.text();

            // 4. IN-MEMORY PARSING LOGIC 
            // Create a temporary div to hold the fetched HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = fragmentText;

            // Find the content for each panel within the temp div
            const middleFragment = tempDiv.querySelector('.content-middle');
            const rightFragment = tempDiv.querySelector('.content-right');

            // 5. INJECTION: Populate the panels
            contentMiddle.innerHTML = middleFragment? middleFragment.innerHTML : `<p>Content for middle panel not found.</p>`;
            contentRight.innerHTML = rightFragment? rightFragment.innerHTML : ``; // Right panel can be empty

            // 6. UX: Scroll both panels back to the top
            contentMiddle.scrollTop = 0;
            contentRight.scrollTop = 0;

        } catch (error) {
            console.error("Fetch Error:", error);
            contentMiddle.innerHTML = `<p class="error">Error loading content. Please check the file path and console.</p>`;
        }
    }

    // Load a introduction page on initial visit
    const initialLink = navPanel.querySelector('a[data-page="01_introduction"]');
    if (initialLink) {
        initialLink.click(); // Programmatically click the first link
    }
});