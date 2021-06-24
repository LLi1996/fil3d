.. _MasksToTrees-label:

Going from 2D to 3D
===================

.. toctree::


We start with:

   * For each velocity channel, a set (python dictionary) of pre-processed masks. We call the container for these masks
     and their corners ``nodes``.

   * An overlap threshold.

   * We also reserve an empty dictionary to store the 3D ``trees`` built from these ``nodes``.


We go through each velocity channel and its associated set of ``nodes`` in order:

   * On the first velocity channel we go through all of the ``nodes`` and initialize a new ``tree`` for each ``node``
     (there are no existing ``tree`` as this moment).

   * For all subsequent velocity channels we:

      * Go through all of the ``nodes``, for each ``node`` we try to match it to an existing ``tree``:

         * To match, we take the dictionary of existing, non-terminated ``tree``, for each ``tree``, we:

            #. Compare the mask overlap between the current ``node`` and the last ``node`` on the ``tree`` (the "last
               ``node``" on the ``tree`` has to be on the previous velocity channel). The comparison is a "two way"
               comparison - we first create a combined (bit-wise AND) overlap mask between the current ``node`` and the
               last ``node`` on the ``tree`` we're trying to match to, then compute the overlap fraction for both the
               (combined mask, current ``node``) pair and the (combined mask, last ``node`` on the ``tree``) pair. If
               the overlap fraction for either pair is greater than our overlap threshold, we consider it to be a match
               and append the current ``node`` onto the ``tree``.

            #. We do this for each existing ``tree``, regardless if the current ``node`` has already matched with a
               ``tree`` - this means that a given ``node`` can match to multiple ``tree``.

            #. This also means that multiple ``nodes`` can match to a given ``tree``. If this does happen (we match the
               current ``node`` to a given ``tree`` that has already matched with another ``node`` on the current
               velocity channel), instead of appending the current ``node`` onto the given ``tree``, we merge the
               current ``node`` with the other ``node`` on the current velocity channel that has also matched with the
               given ``tree`` before doing the append. This is so that, on each velocity channel of the ``tree``, we
               have a "unified" mask.

  * If, after all of this, no match is found for the current ``node``, we initialize a new ``tree`` from the ``node``.

  * Delete all of the terminated trees of length 1 (trees that were initialized by an unmatched ``node`` but didn't
    match with any ``node`` in the next immediate velocity channel). This is to minimize the running number of ``tree``
    we are actively trying to match new ``nodes`` onto.