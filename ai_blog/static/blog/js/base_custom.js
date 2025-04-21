// Custom JS extracted from base.html
// Wait for the DOM to be fully loaded before running scripts
document.addEventListener('DOMContentLoaded', function() {
    // Reading Progress Bar
    const progressBar = document.getElementById('readingProgressBar');
    if (progressBar) {
        const updateProgressBar = () => {
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = document.documentElement.clientHeight;
            const totalHeight = scrollHeight - clientHeight;
            const scrollPosition = window.scrollY || document.documentElement.scrollTop;
            const progress = totalHeight > 0 ? (scrollPosition / totalHeight) * 100 : 0;
            progressBar.style.width = Math.min(progress, 100) + '%';
        };
        window.addEventListener('scroll', updateProgressBar, { passive: true });
        updateProgressBar();
    }
    // Code Block Copy Button
    const codeBlocks = document.querySelectorAll('.post-content pre > code[class*="language-"]');
    codeBlocks.forEach(codeBlock => {
        const preElement = codeBlock.parentElement;
        if (!preElement || preElement.querySelector('.code-header')) return;
        let language = 'code';
        const className = codeBlock.className;
        const match = className.match(/language-(\w+)/);
        if (match && match[1]) language = match[1];
        const header = document.createElement('div');
        header.className = 'code-header';
        const langBadge = document.createElement('span');
        langBadge.className = 'language-badge';
        langBadge.textContent = language.toUpperCase();
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-btn';
        copyButton.setAttribute('aria-label', 'Copy code to clipboard');
        copyButton.innerHTML = '<i class="bi bi-clipboard" aria-hidden="true"></i> Copy';
        copyButton.addEventListener('click', () => {
            const codeToCopy = codeBlock.textContent;
            navigator.clipboard.writeText(codeToCopy).then(() => {
                copyButton.innerHTML = '<i class="bi bi-clipboard-check-fill" aria-hidden="true"></i> Copied!';
                copyButton.disabled = true;
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="bi bi-clipboard" aria-hidden="true"></i> Copy';
                    copyButton.disabled = false;
                }, 2500);
            }).catch(err => {
                console.error('Failed to copy code: ', err);
                copyButton.innerHTML = '<i class="bi bi-x-octagon-fill" aria-hidden="true"></i> Error';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="bi bi-clipboard" aria-hidden="true"></i> Copy';
                }, 2500);
            });
        });
        header.appendChild(langBadge);
        header.appendChild(copyButton);
        preElement.insertBefore(header, codeBlock);
        preElement.setAttribute('role', 'region');
        preElement.setAttribute('aria-label', `${language} code snippet`);
    });
    // Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    // Auto-dismiss alerts
    const alertElements = document.querySelectorAll('.alert-dismissible.fade.show');
    alertElements.forEach(function(alert) {
        if (!alert.classList.contains('alert-danger') && !alert.classList.contains('alert-error')) {
            setTimeout(function() {
                const bsAlert = bootstrap.Alert.getInstance(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 6000);
        }
    });
    // TOC active state
    const tocLinks = document.querySelectorAll('.toc a');
    const headings = document.querySelectorAll('h2, h3, h4');
    if (tocLinks.length > 0 && headings.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const id = entry.target.getAttribute('id');
                if (id) {
                    const tocLink = document.querySelector(`.toc a[href="#${id}"]`);
                    if (tocLink) {
                        if (entry.isIntersecting) {
                            tocLinks.forEach(link => link.parentElement.classList.remove('active'));
                            tocLink.parentElement.classList.add('active');
                        }
                    }
                }
            });
        }, {
            rootMargin: '-100px 0px -80% 0px',
            threshold: 0
        });
        headings.forEach(heading => {
            observer.observe(heading);
        });
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                    history.pushState(null, null, targetId);
                    tocLinks.forEach(l => l.parentElement.classList.remove('active'));
                    this.parentElement.classList.add('active');
                }
            });
        });
        setTimeout(() => {
            window.dispatchEvent(new Event('scroll'));
        }, 200);
    }
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        const setTheme = (isDark) => {
            if (isDark) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        };
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            setTheme(savedTheme === 'dark');
        } else {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            setTheme(prefersDark);
        }
        themeToggle.addEventListener('click', () => {
            const isDark = document.body.classList.contains('dark-mode');
            setTheme(!isDark);
        });
    }

    // Back to Top Button
    const backToTopButton = document.getElementById('back-to-top');
    if (backToTopButton) {
        // Show/hide button based on scroll position
        const toggleBackToTopButton = () => {
            if (window.pageYOffset > 300) { // Show after 300px of scrolling
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        };

        // Scroll to top when clicked
        backToTopButton.addEventListener('click', (e) => {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });

        // Listen for scroll events
        window.addEventListener('scroll', toggleBackToTopButton, { passive: true });

        // Initial check
        toggleBackToTopButton();
    }

    // Copy link to clipboard functionality for social sharing
    const copyLinkBtn = document.getElementById('copy-link');
    if (copyLinkBtn) {
        copyLinkBtn.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            
            navigator.clipboard.writeText(url).then(() => {
                // Show success state
                copyLinkBtn.classList.add('copied');
                const originalIcon = copyLinkBtn.innerHTML;
                copyLinkBtn.innerHTML = '<i class="bi bi-check2"></i>';
                
                // Reset after 2 seconds
                setTimeout(() => {
                    copyLinkBtn.classList.remove('copied');
                    copyLinkBtn.innerHTML = originalIcon;
                }, 2000);
                
                // Update tooltip text if tooltip is initialized
                const tooltip = bootstrap.Tooltip.getInstance(copyLinkBtn);
                if (tooltip) {
                    tooltip.setContent({ '.tooltip-inner': 'Copied!' });
                    
                    // Reset tooltip text after 2 seconds
                    setTimeout(() => {
                        tooltip.setContent({ '.tooltip-inner': 'Copy link' });
                    }, 2000);
                }
            }).catch(err => {
                console.error('Failed to copy: ', err);
                
                // Show error state
                const originalIcon = copyLinkBtn.innerHTML;
                copyLinkBtn.innerHTML = '<i class="bi bi-exclamation-triangle"></i>';
                
                // Reset after 2 seconds
                setTimeout(() => {
                    copyLinkBtn.innerHTML = originalIcon;
                }, 2000);
            });
        });
    }

    // Automatic Table of Contents Generator for Blog Posts
    const tocContainer = document.getElementById('tocContainer');
    const postContent = document.querySelector('.post-content');
    
    if (tocContainer && postContent) {
        // Find all headings in the post content (h2, h3, h4)
        const headings = postContent.querySelectorAll('h2, h3, h4');
        
        if (headings.length > 0) {
            // Remove placeholder loading elements
            tocContainer.innerHTML = '';
            
            // Create the list
            const tocList = document.createElement('ul');
            tocList.className = 'list-unstyled mb-0';
            
            // Track heading levels for proper nesting
            let currentLevel = 0;
            let currentList = tocList;
            let listStack = [tocList];
            
            headings.forEach((heading, index) => {
                // Add id to heading if it doesn't have one
                if (!heading.id) {
                    heading.id = `heading-${index}`;
                }
                
                // Get heading level number (2 for h2, 3 for h3, etc.)
                const level = parseInt(heading.tagName.substring(1));
                
                // Create list item
                const listItem = document.createElement('li');
                
                // Create link
                const link = document.createElement('a');
                link.href = `#${heading.id}`;
                link.textContent = heading.textContent;
                link.setAttribute('data-heading-id', heading.id);
                
                // Append link to list item
                listItem.appendChild(link);
                
                // Handle nesting based on heading level
                if (level > currentLevel) {
                    // Need to go deeper - create new nested list
                    const nestedList = document.createElement('ul');
                    listStack[listStack.length - 1].lastChild.appendChild(nestedList);
                    listStack.push(nestedList);
                    currentList = nestedList;
                } else if (level < currentLevel) {
                    // Need to go up - pop lists from stack
                    while (level < currentLevel && listStack.length > 1) {
                        listStack.pop();
                        currentLevel--;
                    }
                    currentList = listStack[listStack.length - 1];
                }
                
                // Add list item to current list
                currentList.appendChild(listItem);
                currentLevel = level;
            });
            
            // Add the TOC to the container
            tocContainer.appendChild(tocList);
            
            // Make the TOC sticky if the post is long enough
            const postHeight = postContent.offsetHeight;
            if (postHeight > window.innerHeight * 1.5) {
                document.querySelector('.toc').classList.add('sticky-toc');
            }
        } else {
            // If no headings, hide the TOC
            const tocCard = tocContainer.closest('.toc');
            if (tocCard) {
                tocCard.style.display = 'none';
            }
        }
    }
});
