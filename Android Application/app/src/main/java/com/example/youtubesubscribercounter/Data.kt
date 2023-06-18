package com.example.youtubesubscribercounter

import com.google.gson.annotations.SerializedName

data class SearchResponse(
    @SerializedName("items") val items: List<Search>?
)

data class ChannelResponse(
    @SerializedName("items") val items: List<Channel>?
)

data class Search(
    @SerializedName("id") val id: ID?,
    @SerializedName("snippet") val snippet: Snippet?,
    @SerializedName("statistics") val statistics: Statistics?
)

data class Channel(
    @SerializedName("id") val id: String?,
    @SerializedName("snippet") val snippet: Snippet?,
    @SerializedName("statistics") val statistics: Statistics?
)

data class Snippet(
    @SerializedName("title") val title: String?,
    @SerializedName("thumbnails") val thumbnails: Thumbnail?
)

data class Thumbnail(
    @SerializedName("default") val default: Default?
)

data class Default(
    @SerializedName("url") val url: String?
)

data class Statistics(
    @SerializedName("viewCount") val viewCount: Long?,
    @SerializedName("subscriberCount") val subscriberCount: Long?,
    @SerializedName("videoCount") val videoCount: Long?
)

data class ID(
    @SerializedName("channelId") val channelID: String?
)