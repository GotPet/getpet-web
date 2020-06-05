
/**
 * Load required plugins.
 */
require('waypoints/lib/jquery.waypoints');
import { CountUp } from 'countup.js';

/**
 * Configure the plugin.
 */

+function($){
  page.registerVendor('Countup');

  page.initCountup = function() {

    $('[data-provide~="countup"]:not(.counted)').each(function() {
      var tag = $(this);
      var extraOptions = {};
      extraOptions = $.extend( extraOptions, page.getDataOptions(tag));

      var options = {
        startVal: tag.dataAttr('from', 0),
        endVal:   tag.dataAttr('to', 0),
        options:  extraOptions,
      };
      options = $.extend( options, page.getDataOptions(tag));

      tag.waypoint({
        handler: function($direction) {
          tag.countup(options).addClass('counted');
        },
        offset: '100%'
      });

    });

  }

}(jQuery);



(function ($) {
  $.fn.countup = function (params) {
    // make sure dependency is present
    if (typeof CountUp !== 'function') {
      console.error('countUp.js is a required dependency of countUp-jquery.js.');
      return;
    }
    
    var defaults = {
      startVal: 0,
      decimalPlaces: 0,
      duration: 4,
    };

    if (typeof params === 'number') {
      defaults.endVal = params;
    }
    else if (typeof params === 'object') {
      $.extend(defaults, params);
    }
    else {
      console.error('countUp-jquery requires its argument to be either an object or number');
      return;
    }

    this.each(function (i, elem) {
      var countUp = new CountUp(elem, defaults.endVal, defaults.options);
      countUp.start();
    });

    return this;
  };

}(jQuery));