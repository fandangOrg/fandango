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