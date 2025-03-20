function ApplyObserver(className, elementToAnimate) {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    elementToAnimate.classList.add(className);
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.5 }
    );
    return observer;
}

const openSignupPage = () => {
    window.location.href = "pricing.html";
};

window.onscroll = function () {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        backToTOp.style.display = "block";
    } else {
        backToTOp.style.display = "none";
    }
  };



document.addEventListener("DOMContentLoaded", () => {
    const signupButton = document.querySelector(".left-animation-button");
    const section4 = document.querySelector(".section4");
    const section3 = document.querySelector(".section3");
    const hidden_right = document.querySelectorAll(".hidden-right");
    const hidden_left = document.querySelectorAll(".hidden-left");
    const opacity_hidden = document.querySelectorAll(".opacity-hidden");
    const backToTOp = document.getElementById("backToTopBtn");


    

      backToTOp.addEventListener("click", () => {
        document.body.scrollTop = 0;
        document.documentElement.scrollTop = 0;
      });

      
    opacity_hidden.forEach((el) => {
        const opacityObserver = ApplyObserver('opacity-show', el);
        opacityObserver.observe(el);
    });
    

    const signupObserver = ApplyObserver('show', signupButton);
    signupObserver.observe(section4);

    hidden_right.forEach((el) => {
        const rightObserver = ApplyObserver('show', el); 
        rightObserver.observe(section3);
    });

    hidden_left.forEach((el) => { 
        const leftObserver = ApplyObserver('show', el); 
        leftObserver.observe(section3);
    });

  
});