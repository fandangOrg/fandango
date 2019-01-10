annotation.directive("appNavbar", function () {
    return {
        templateUrl: 'navbar.html'
    };
});

annotation.directive("appFooter", function () {
    return {
        templateUrl: 'footer.html'
    };
});

annotation.directive("articleCheckerManual", function () {
    return {
        templateUrl: 'article_checker_manual.html'
    }
});

annotation.directive("articleCheckerAuto", function () {
    return {
        templateUrl: 'article_checker_auto.html'
    }
});

annotation.directive("articleCheckerDomain", function () {
    return {
        templateUrl: 'article_checker_domain.html'
    }
});

annotation.directive("articleAnalysis", function () {
    return {
        templateUrl: 'article_analysis.html'
    }
});
