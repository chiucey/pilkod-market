/* ===================================================================
 * base.js — Physical Content Display 通用滚动触发动画
 * 用途：AI 代理制作成品 HTML 时，将本文件全部内容复制到 <script> 块中
 * 注意：必须与 base.css 中的 .anim-* 类配合使用
 * =================================================================== */
(function(){
  const animateElements = document.querySelectorAll('.anim-fade-up, .anim-fade-left, .anim-fade-right, .anim-scale-in, .anim-stagger-list');
  const observer = new IntersectionObserver(function(entries){
    entries.forEach(entry => {
      if(entry.isIntersecting){
        entry.target.classList.add('is-visible');
        entry.target.classList.remove('is-exiting');
      } else {
        entry.target.classList.add('is-exiting');
        entry.target.classList.remove('is-visible');
      }
    });
  }, { threshold: 0.15 });
  animateElements.forEach(el => observer.observe(el));
})();

/* 导航栏滚动高亮 — 所有成品必须包含 */
(function(){
  var sections = document.querySelectorAll('.scroll-section[id]');
  var links = document.querySelectorAll('.nav-bar a');
  function update(){
    var scrollY = window.scrollY + 100;
    var activeId = '';
    sections.forEach(function(s){
      if(s.offsetTop <= scrollY) activeId = s.id;
    });
    links.forEach(function(a){
      a.classList.toggle('active', a.getAttribute('href') === '#' + activeId);
    });
  }
  window.addEventListener('scroll', update);
  update();
})();
