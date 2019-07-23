export default function (kibana) {
  return new kibana.Plugin({
    require: ['kibana'],
    id: 'custom_css',

    uiExports: {
      hacks: [
        'plugins/custom_css/index',
      ]
    }
  });
};
