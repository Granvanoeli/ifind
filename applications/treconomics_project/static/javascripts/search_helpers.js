/*

Search Helpers for Treconomics - used for all types of search.

Author: David Maxwell
Date: 2013-11-13
Revision: 1

*/

$(function() {
    bindResultHovering();
    changePointer();

    if ($('#query')) {
        $('#query').focus();
    }
});

/*
Bind hovers over search result elements.
Logs the event with an AJAX call for hovering in and a call for hovering out.
*/
function bindResultHovering() {
    $('.search_result').hover(
        function(event) {
            var parent = $(event.target).closest('div[class="search_result"]');
            var trecID = $(parent[0]).attr('id');
            var whooshID = $(parent[0]).attr('whooshid');
            var rank = $(parent[0]).attr('rank');
            var page = $(parent[0]).attr('page');

            $.ajax({
                url: APP_ROOT + 'hover/',
                data: {'status': 'in', 'trecID': trecID, 'whooshID': whooshID, 'rank': rank, 'page': page}
            });
        },
        function(event) {
            var parent = $(event.target).closest('div[class="search_result"]');
            var trecID = $(parent[0]).attr('id');
            var whooshID = $(parent[0]).attr('whooshid');
            var rank = $(parent[0]).attr('rank');
            var page = $(parent[0]).attr('page');

            $.ajax({
                url: APP_ROOT + 'hover/',
                data: {'status': 'out', 'trecID': trecID, 'whooshID': whooshID, 'rank': rank, 'page': page}
        });
    });
}

function changePointer() {
    $("#search_form").submit(function(event) {
        $('*').css('cursor', 'progress');

        // If they are present, close all autocomplete boxes upon form submission.

        if ($('.searchbox').hasClass('ui-autocomplete-input')) {
            $('.searchbox').autocomplete('close');
        }

        if ($('.smallsearchbox').hasClass('ui-autocomplete-input')) {
            $('.smallsearchbox').autocomplete('close');
        }
    });
}