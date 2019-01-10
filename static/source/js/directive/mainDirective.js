app.directive("appNavbar", function() {
    return {
        templateUrl : 'navbar.html'
    };
});

app.directive("appFooter", function() {
    return {
        templateUrl : 'footer.html'
    };
});

app.directive("articleChecker", function () {
  return {
      templateUrl : 'article_checker.html'
  }
});

app.directive("articleCheckerManual", function () {
    return {
        templateUrl : 'article_checker_manual.html'
    }
});

app.directive("articleCheckerAuto", function () {
    return {
        templateUrl : 'article_checker_auto.html'
    }
});

app.directive("articleCheckerDomain", function () {
    return {
        templateUrl : 'article_checker_domain.html'
    }
});

app.directive("articleAnalysis", function () {
    return {
        templateUrl : 'article_analysis.html'
    }
});

app.directive("articleAnalysisFakeness", function () {
    return {
        templateUrl : 'article_analysis_fakeness.html'
    }
});