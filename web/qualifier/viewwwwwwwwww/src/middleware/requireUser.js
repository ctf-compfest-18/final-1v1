function requireUser(authService) {
  return (req, res, next) => {
    const user = authService.findUser(req.session.userId);

    if (!user) {
      req.session.userId = null;
      return res.redirect("/login");
    }

    req.user = user;
    res.locals.user = user;
    return next();
  };
}

module.exports = { requireUser };
