console.log 'story.coffee'

$story_cover = $('.item_cover')
$story_title = $('.story_title')

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
$(window).on 'resize', ->
    positionTitle()
