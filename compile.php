<?php

use Puneetxp\CompilePhp\Compile\compilephp;
require "./vendor/autoload.php";
(new compilephp("Resource/View", __DIR__))->run();
