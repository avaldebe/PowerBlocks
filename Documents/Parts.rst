Blocks, Modules and Assemblies
==============================

Blocks are independent units that can be easily combined to form
different devices. They are composed of Modules and Assemblies, which
are common to different Blocks and can be easily
swapped/exchanged/replaced. Modules are ready made items that can easily
be purchased, such as a panel meter. Assemblies DIY jigs made of common
parts.


Modules
-------

Panel meter
~~~~~~~~~~~

There are plenty to choose from

============ =========== ======== ======== ======================== ==========
Display      dimensions  voltage  current  other                    source
============ =========== ======== ======== ======================== ==========
OLED         47x28x21 mm 100.00 V 15.000 A time, power, temperature `$7`__
OLED         48x29x22 mm 33.00 V  3.000 A  time, power, temperature `$10/2`__
Red+Blue LED 48x29x22 mm 33.00 V  3.000 A  0.1 mA resol. below 1 A  `$7`__
Red LED      48x29x22 mm 33.00 V  3.000 A                           `$13/4`__
============ =========== ======== ======== ======================== ==========

.. __: https://www.aliexpress.com/snapshot/8413414312.html?spm=2114.13010608.0.0.EBPhpS&orderId=80142073330843&productId=32732985387
.. __: https://www.aliexpress.com/snapshot/6722220227.html?spm=2114.13010608.0.0.6rTZ9H&orderId=67697992120843&productId=32363192222
.. __: https://www.aliexpress.com/snapshot/6259249925.html?spm=2114.13010608.0.0.bMkVlW&orderId=63943819130843&productId=1702880664
.. __: https://www.aliexpress.com/snapshot/6624872566.html?spm=2114.13010608.0.0.6rTZ9H&orderId=66919764180843&productId=32240698328

DC converter
~~~~~~~~~~~~

Short list of available modules

============= ========== ======= ============= ======= ======
IC(s)         topology   input   output[1]_        control source
============= ========== ======= ============= ======= ======
LM2577 LM2596 boost buck 4-35V   1.25-25V/2A   CV/CC   `$5`__
              buck       4.5-24V 0.8-17V/1.5A  CV      `$3/5`__
MT3608        boost      2-24V   28V/2A        CV      `$0.4`__
XL6009        SEPIC      5-32V   1.25-35V/1.5A CV      `$1.3`__
============= ========== ======= ============= ======= ======

.. __: https://www.aliexpress.com/snapshot/6259934254.html?spm=2114.13010608.0.0.ZKrSb3&orderId=63944214630843&productId=1823405838
.. __: https://www.aliexpress.com/snapshot/8238855247.html?spm=2114.13010608.0.0.ZKrSb3&orderId=79252067950843&productId=32749335208
.. __: https://www.aliexpress.com/snapshot/8210617364.html?spm=2114.13010608.0.0.ZTfNaG&orderId=79013326890843&productId=32365423320
.. __: http://www.ebay.com/sch/sis.html?_nkw=Hot+Selling+DC-DC+Boost+Buck+Step+Down+Up+Converter+XL6009+Solar+Voltage+Module&_id=301596262442&&_trksid=p2057872.m2749.l2658
.. [1] Missing test/benchmark info

DC supply
~~~~~~~~~

Short list of DC convertes with display, that can be used as a bench supply.

====== ======== ===== =========== ======= ======
model  topology input  output[1]_ control source
====== ======== ===== =========== ======= ======
B3603  buck     6-40V 36V/3A      CV/CC   `$10`__
B3606  buck     6-40V 36V/6A      CV/CC   `$14`__
BST400 boost    6-40V 80V/10A     CV/CC   `$23`__
       buck     5-23V 16V/3A      CV      `$6`__
====== ======== ===== =========== ======= ======

.. __: http://www.banggood.com/search/b3603.html
.. __: http://www.banggood.com/search/b3606.html
.. __: http://www.banggood.com/search/946745.html
.. __: http://www.banggood.com/search/1038740.html


Assemblies
----------

Tools
-----

Other parts
-----------

.. _`volt meter`:  https://www.aliexpress.com/snapshot/8027565918.html?spm=2114.13010608.0.0.6rTZ9H&orderId=77802306580843&productId=1148697683
.. _`fuse holder`: https://www.aliexpress.com/snapshot/6438857005.html?spm=2114.13010608.0.0.bMkVlW&orderId=65341668590843&productId=2034813391


9v batteries
~~~~~~~~~~~~

Rechargeable 9v (E) batteries are great for portable projects. Recently
2S1P lipo batteries (7.4v) in 9v form factor have appeared, aimed to the
RC/FVP market. In addition to protection and balance circuitry, they
contain USB charging, charge indicator LEDs.

========= ============= ======= ============ =========
connector chemistry     voltage capacity[*]_ source
========= ============= ======= ============ =========
DC jack   lipo (2S)     7.4 V   5.92 Wh      `$11`__
9V snaps  lipo (2S)     7.4 V   2.96 Wh      `$13/2`__
9V snaps  NiMH (HR6F22) 8.4 V   1.68 Wh      `$15`__
========= ============= ======= ============ =========

.. __: http://www.banggood.com/search/1049185.html
.. __: http://www.banggood.com/search/1101430.html
.. __: https://www.kjell.com/no/sok?query=42710
.. [*] As usual with lipo batteries, capacity claims
       are misleading/wrong... To be updated
