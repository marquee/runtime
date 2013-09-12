
_buildIframeEmbed = (url, attrs={}) ->
    attributes = []
    for k, v of attrs
        attributes.push("k='#{ v }'")
    attributes = attributes.join(' ')
    return "<iframe src='#{ url }' frameborder='0' #{ attributes } webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>"

class EmbedCover
    constructor: (el) ->
        @$el = $(el)

        url = @$el.attr('data-embed_url')
        if url
            @_url = URI(url)
            if not @_url.protocol()
                @_url = URI("http://#{ url }")
            if not @_url.hostname()
                @_url = null

        if @_url
            @_buildEmbed()
        else
            @_buildFallback()


    _buildFallback: ->
        try
            cover_urls = JSON.parse(@$el.attr('data-cover_urls'))
        catch e
            console.error(e)
        if cover_urls
            @$el.css
                'background-image': "url(#{ cover_urls['1280'] })"
        else
            @$el.remove()


    _buildEmbed: ->
        hostname = @_url.hostname().split('.')
        if hostname[0] is 'www'
            hostname.shift()
        hostname = hostname.join('.')
        console.log hostname
        switch hostname
            when 'youtube.com'
                embed = _buildIframeEmbed("http://www.youtube.com/embed/#{ @_url.query(true).v }?controls=0&modestbranding=1&showinfo=0")
            when 'vimeo.com'
                embed = _buildIframeEmbed("#{ @_url.protocol() }://player.vimeo.com/video#{ @_url.path() }")
        if embed
            @_renderEmbed(embed)


    _renderEmbed: (embed) ->
        @$el.addClass('EmbedCover')
        @$el.append(embed)


$('[data-cover_type="embed"]').each (i, el) ->
    new EmbedCover(el)