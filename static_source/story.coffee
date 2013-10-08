console.log 'story.coffee'

$window = $(window)

$story_cover = $('#story_title .item_cover')
$story_title = $('#story_title .item_title')

# Draw title in correct place
calculateTitlePos = (cover_height) ->
    top_pos = cover_height - (cover_height / 2) - $story_title.height()
    return top_pos


positionTitle = ->
    cover_height = $story_cover.height()
    top_pos = calculateTitlePos(cover_height)
    $story_title.css
        top: top_pos

positionTitle()
$window.on 'resize', ->
    positionTitle()


# Load covers for related content
$related_content = $('#story_related_content')
related_covers_loaded = false
$window.on 'scroll', _.debounce (e) ->
    if $window.scrollTop() > $related_content.offset()?.top * 0.75 and not related_covers_loaded
        related_covers_loaded = true
        $related_content.find('[data-cover_content_id]').each (i, el) ->
            $el = $(el)
            # Not sure why the story object in the template doesn't have the full URL.
            # So, building it manually :(
            id = $el.attr('data-cover_content_id')
            url = "//#{ window.params.CONTENT_API_ROOT }#{ id }"
            $.ajax
                url: url
                data:
                    token: window.params.READER_TOKEN
                success: (response) ->
                    $el.find('.item_cover').css
                        'background-image'  : "url(#{ response.content['640'].url })"
, 20
