'use strict';

const Module = require('module');
const path = require('path');

const originalLoad = Module._load;

Module._load = function (request, parent, isMain) {
  if (request === '@sec/cliguard') {
    return originalLoad(
      path.join(__dirname, 'cliguard', 'index.js'),
      parent,
      isMain
    );
  }

  return originalLoad(request, parent, isMain);
};

require(path.join(__dirname, 'runtime', 'index.js'));
