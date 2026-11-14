// Small progressive enhancement: highlight the section currently being viewed.
const sections = [...document.querySelectorAll('main section[id]')];
const links = [...document.querySelectorAll('.sidebar nav a')];
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      links.forEach(link => link.classList.toggle('active', link.hash === `#${entry.target.id}`));
    }
  }, { rootMargin: '-15% 0px -70% 0px' });
  sections.forEach(section => observer.observe(section));
}
