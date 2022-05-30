(function webpackUniversalModuleDefinition(root, factory) {
	if(typeof exports === 'object' && typeof module === 'object')
		module.exports = factory();
	else if(typeof define === 'function' && define.amd)
		define([], factory);
	else if(typeof exports === 'object')
		exports["centraldashboard"] = factory();
	else
		root["centraldashboard"] = factory();
})(window, function() {
return /******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = "./public/library.js");
/******/ })
/************************************************************************/
/******/ ({

/***/ "./public/library.js":
/*!***************************!*\
  !*** ./public/library.js ***!
  \***************************/
/*! exports provided: PARENT_CONNECTED_EVENT, IFRAME_CONNECTED_EVENT, NAMESPACE_SELECTED_EVENT, MESSAGE, CentralDashboardEventHandler */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "PARENT_CONNECTED_EVENT", function() { return PARENT_CONNECTED_EVENT; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "IFRAME_CONNECTED_EVENT", function() { return IFRAME_CONNECTED_EVENT; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "NAMESPACE_SELECTED_EVENT", function() { return NAMESPACE_SELECTED_EVENT; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "MESSAGE", function() { return MESSAGE; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "CentralDashboardEventHandler", function() { return CentralDashboardEventHandler; });
/**
 * @fileoverview Library for use with pages that need to communicate with the
 * Central Dashboard.
 */
const PARENT_CONNECTED_EVENT = 'parent-connected';
const IFRAME_CONNECTED_EVENT = 'iframe-connected';
const NAMESPACE_SELECTED_EVENT = 'namespace-selected';
const MESSAGE = 'message';
/**
 * Encapsulates the sending, receiving, and handling of events between iframed
 * pages and the CentralDashboard component. Events data should a type property
 * indicating the type of message and a value property with the payload.
 */

class CentralDashboardEventHandler_ {
  constructor() {
    this.window = window;
    this.parent = window.parent;
    this._messageEventListener = null;
    this._onParentConnected = null;
    this._onNamespaceSelected = null;
  }
  /**
   * Invokes the supplied callback function, then establishes the
   * communication with the parent frame.
   * @param {Function} callback - Callback invoked with this instance and a
   *  boolean indicating whether the page importing the library is iframed.
   * @param {boolean} disableForceIframe - In case DASHBOARD_FORCE_IFRAME
   *  is set to true, forcing every app to be iframed, set this flag to avoid
   *  the redirection.
   */


  init(callback, disableForceIframe = false) {
    const isIframed = this.window.location !== this.parent.location;
    callback(this, isIframed);

    if (isIframed) {
      this._messageEventListener = this._onMessageReceived.bind(this);
      this.window.addEventListener(MESSAGE, this._messageEventListener);
      this.parent.postMessage({
        type: IFRAME_CONNECTED_EVENT
      }, this.parent.origin);
    } else if (!disableForceIframe) {
      fetch('/api/dashboard-settings').then(res => res.json()).then(data => {
        if (data.DASHBOARD_FORCE_IFRAME) {
          // pre-pend `/_/` to navigate to central dashboard
          const newLoc = this.window.location.origin + this.window.location.href.replace(this.window.location.origin, '/_');
          this.window.location.replace(newLoc);
        }
      }) // eslint-disable-next-line no-console
      .catch(err => console.error(err));
    }
  }
  /**
   * Removes the message event listener.
   */


  detach() {
    if (this._messageEventListener) {
      this.window.removeEventListener(MESSAGE, this._messageEventListener);
    }
  }
  /**
   * Attaches a callback function to respond to the PARENT_CONNECTED_EVENT
   * event.
   * @param {Function} callback - Callback accepting an object that contains
   *  the event data.
   */


  set onParentConnected(callback) {
    if (typeof callback === 'function') {
      this._onParentConnected = callback;
    }
  }
  /**
   * Attaches a callback function to respond to the NAMESPACE_SELECTED_EVENT
   * event.
   * @param {Function} callback - Callback accepting an object that contains
   *  the event data.
   */


  set onNamespaceSelected(callback) {
    if (typeof callback === 'function') {
      this._onNamespaceSelected = callback;
    }
  }
  /**
   * Handle the receipt of a message and dispatch to any added callbacks.
   * @param {MessageEvent} event
   */


  _onMessageReceived(event) {
    const {
      data
    } = event;

    switch (data.type) {
      case PARENT_CONNECTED_EVENT:
        if (this._onParentConnected) {
          this._onParentConnected(data);
        }

        break;

      case NAMESPACE_SELECTED_EVENT:
        if (this._onNamespaceSelected) {
          this._onNamespaceSelected(data.value);
        }

        break;
    }
  }

} // Exports a singleton instance


const CentralDashboardEventHandler = new CentralDashboardEventHandler_();

/***/ })

/******/ });
});
//# sourceMappingURL=dashboard_lib.bundle.js.map