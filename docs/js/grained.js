/*!
 * Grained.js
 * Author : Sarath Saleem - https://github.com/sarathsaleem
 * GitHub : https://github.com/sarathsaleem/grained
 */

(function (window, doc) {
    "use strict";

    function grained(ele, opt) {
        var element = null,
            elementId = null;

        // Handle string or DOM element input
        if (typeof ele === 'string') {
            element = doc.getElementById(ele.split('#')[1]);
        } else if (typeof ele === 'object') {
            element = ele;
        }

        if (!element) {
            console.error('Grained: cannot find the element with id ' + ele);
            return;
        } else {
            elementId = element.id;
        }

        // Set style for parent element
        if (element.style.position !== 'absolute') {
            element.style.position = 'relative';
        }
        element.style.overflow = 'hidden';

        // Default options
        var options = {
            animate: true,
            patternWidth: 100,
            patternHeight: 100,
            grainOpacity: 0.05,
            grainDensity: 1,
            grainWidth: 1,
            grainHeight: 1,
            grainChaos: 0.5,
            grainSpeed: 20
        };

        // Merge user options with defaults
        Object.keys(opt).forEach(function (key) {
            options[key] = opt[key];
        });

        // Generate noise using canvas
        var generateNoise = function () {
            var canvas = doc.createElement('canvas');
            var ctx = canvas.getContext('2d');
            canvas.width = options.patternWidth;
            canvas.height = options.patternHeight;

            for (var w = 0; w < options.patternWidth; w += options.grainDensity) {
                for (var h = 0; h < options.patternHeight; h += options.grainDensity) {
                    var rgb = Math.random() * 256 | 0;
                    ctx.fillStyle = 'rgba(' + [rgb, rgb, rgb, options.grainOpacity].join() + ')';
                    ctx.fillRect(w, h, options.grainWidth, options.grainHeight);
                }
            }
            return canvas.toDataURL('image/png');
        };

        // Function to add grain div
        function addGrainDiv() {
            var grainDiv = doc.createElement('div');
            grainDiv.className = 'grained';
            
            // Create base64 noise image
            var dataURI = generateNoise();

            // Set styles for the grain overlay
            grainDiv.style.cssText = [
                'position: absolute',
                'top: -50%',
                'left: -50%',
                'right: -50%',
                'bottom: -50%',
                'width: 200%',
                'height: 200%',
                'background-image: url(' + dataURI + ')',
                'background-repeat: repeat',
                'pointer-events: none',
                'opacity: 1',
                'z-index: 1'
            ].join(';');

            // Add animation if enabled
            if (options.animate) {
                // Create keyframes
                var animationName = 'grained-animation-' + elementId;
                var keyframes = '@keyframes ' + animationName + ' {' +
                    '0%, 100% { transform: translate(0, 0); }' +
                    '10% { transform: translate(-5%, -10%); }' +
                    '20% { transform: translate(-15%, 5%); }' +
                    '30% { transform: translate(7%, -25%); }' +
                    '40% { transform: translate(-5%, 25%); }' +
                    '50% { transform: translate(-15%, 10%); }' +
                    '60% { transform: translate(15%, 0%); }' +
                    '70% { transform: translate(0%, 15%); }' +
                    '80% { transform: translate(3%, 35%); }' +
                    '90% { transform: translate(-10%, 10%); }' +
                '}';

                // Add keyframes to document
                var style = doc.createElement('style');
                style.type = 'text/css';
                style.innerHTML = keyframes;
                doc.getElementsByTagName('head')[0].appendChild(style);

                // Apply animation to grain div
                grainDiv.style.animation = animationName + ' ' + options.grainSpeed + 's steps(10, end) infinite';
            }

            // Insert grain div as first child
            element.insertBefore(grainDiv, element.firstChild);
        }

        // Add grain effect
        addGrainDiv();

        console.log('Grained effect applied to #' + elementId);
    }

    // Export to window
    window.grained = grained;

})(window, document);
