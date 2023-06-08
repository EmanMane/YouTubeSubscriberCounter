package com.example.youtubesubscribercounter

import retrofit2.Call
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*


object YouTubeApiConfig {
    internal val retrofit: YouTubeApi = Retrofit.Builder()
        .baseUrl("https://www.googleapis.com/youtube/v3/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(YouTubeApi::class.java)
}


interface YouTubeApi {
    @GET("search")
    fun getChannelsByHandle(
        @Query("part") part: String,
        @Query("maxResults") maxResults: Int,
        @Query("type") type: String,
        @Query("q") query: String?,
        @Query("key") apiKey: String
    ): Call<SearchResponse>?

    @GET("channels")
    fun getChannelDetails(
        @Query("part") part: String,
        @Query("id") channelId: String,
        @Query("key") apiKey: String
    ): Call<ChannelResponse>?

}
