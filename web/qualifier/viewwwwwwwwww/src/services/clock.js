class Clock {
  constructor(locale = "en") {
    this.formatter = new Intl.DateTimeFormat(locale, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
  }

  timeLabel() {
    return this.formatter.format(new Date());
  }
}

module.exports = { Clock };
