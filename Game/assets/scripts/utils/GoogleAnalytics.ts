declare var gtag: Function;

function sendAnalyticsEvent(
  action: string,
  category: string,
  label: string,
  value?: number | string
) {
  if (typeof gtag === "function") {
    gtag("event", action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  } else {
    console.error("Google Analytics is not initialized.");
  }
}

export { sendAnalyticsEvent };
